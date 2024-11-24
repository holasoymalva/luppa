import streamlit as st
import networkx as nx
import pandas as pd
import anthropic
import json
import plotly.graph_objects as go
from pathlib import Path
import PyPDF2
import io
from datetime import datetime
import numpy as np

class CorruptionNetworkAnalyzer:
    def __init__(self, api_key):
        """Inicializa el analizador con la API key de Anthropic"""
        self.client = anthropic.Client(api_key)
        self.graph = nx.Graph()
        self.entities = {}
        self.relationships = []
        
    def process_document(self, document_text, document_type):
        """Procesa un documento usando Claude para extraer entidades y relaciones"""
        prompt = f"""Analiza el siguiente documento y extrae todas las entidades y relaciones relevantes.
        Tipo de documento: {document_type}
        
        Busca específicamente:
        1. Funcionarios públicos (nombres, cargos, dependencias)
        2. Empresas contratistas (nombres, RFC, montos)
        3. Beneficiarios de programas (nombres, beneficios recibidos)
        4. Personas políticamente expuestas (nombres, roles)
        5. Relaciones entre estas entidades
        
        Documento:
        {document_text}
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "entities": [
                {{
                    "id": "string",
                    "name": "string",
                    "type": "funcionario|empresa|beneficiario|ppe",
                    "attributes": {{}}
                }}
            ],
            "relationships": [
                {{
                    "source": "entity_id",
                    "target": "entity_id",
                    "type": "familiar|comercial|politica|beneficio",
                    "attributes": {{}}
                }}
            ]
        }}
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content)
            self._update_graph(result)
            return result
        except Exception as e:
            st.error(f"Error procesando documento: {str(e)}")
            return None
    
    def _update_graph(self, analysis_result):
        """Actualiza el grafo con nuevas entidades y relaciones"""
        # Agregar entidades
        for entity in analysis_result['entities']:
            self.graph.add_node(
                entity['id'],
                **entity['attributes'],
                node_type=entity['type'],
                name=entity['name']
            )
            self.entities[entity['id']] = entity
            
        # Agregar relaciones
        for rel in analysis_result['relationships']:
            self.graph.add_edge(
                rel['source'],
                rel['target'],
                **rel['attributes'],
                relationship_type=rel['type']
            )
            self.relationships.append(rel)
    
    def detect_suspicious_patterns(self):
        """Detecta patrones sospechosos en la red"""
        suspicious_patterns = []
        
        # Detectar ciclos cerrados entre funcionarios y empresas
        cycles = nx.cycle_basis(self.graph)
        for cycle in cycles:
            if len(cycle) >= 3:  # Ciclos de 3 o más nodos
                cycle_types = [self.entities[node]['type'] for node in cycle]
                if 'funcionario' in cycle_types and 'empresa' in cycle_types:
                    suspicious_patterns.append({
                        'type': 'ciclo_sospechoso',
                        'nodes': cycle,
                        'description': 'Ciclo cerrado entre funcionarios y empresas'
                    })
        
        # Detectar concentración de contratos
        empresa_degrees = {
            node: degree for node, degree in self.graph.degree()
            if self.entities[node]['type'] == 'empresa'
        }
        if empresa_degrees:
            mean_degree = np.mean(list(empresa_degrees.values()))
            std_degree = np.std(list(empresa_degrees.values()))
            
            for empresa, degree in empresa_degrees.items():
                if degree > mean_degree + 2 * std_degree:
                    suspicious_patterns.append({
                        'type': 'concentracion_contratos',
                        'node': empresa,
                        'degree': degree,
                        'description': 'Concentración anormal de contratos'
                    })
        
        return suspicious_patterns
    
    def generate_network_visualization(self):
        """Genera una visualización de la red usando Plotly"""
        pos = nx.spring_layout(self.graph)
        
        # Configurar nodos
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                size=20,
                color=[],
                colorscale='Viridis',
                line_width=2))

        # Configurar enlaces
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        # Agregar posiciones de nodos
        for node in self.graph.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_info = self.entities[node]
            node_trace['text'] += tuple([f"{node_info['name']}\n({node_info['type']})"])
            
            # Color por tipo de entidad
            color_map = {
                'funcionario': 0,
                'empresa': 0.33,
                'beneficiario': 0.66,
                'ppe': 1
            }
            node_trace['marker']['color'] += tuple([color_map[node_info['type']]])

        # Agregar enlaces
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])

        # Crear figura
        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                        title='Red de Relaciones',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
        return fig

def main():
    st.set_page_config(page_title="Analizador de Redes de Corrupción", layout="wide")
    
    st.title("Analizador de Redes de Corrupción")
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("Configuración")
        api_key = st.text_input("API Key de Anthropic", type="password")
        
        if not api_key:
            st.warning("Por favor, ingresa tu API Key de Anthropic")
            return
            
        analyzer = CorruptionNetworkAnalyzer(api_key)
    
    # Sección de carga de documentos
    st.header("Carga de Documentos")
    
    doc_type = st.selectbox(
        "Tipo de Documento",
        ["Declaración Patrimonial", "Contrato Público", "Lista de Beneficiarios", "Otro"]
    )
    
    uploaded_file = st.file_uploader("Cargar documento", type=["txt", "pdf"])
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        else:
            text = uploaded_file.read().decode()
            
        if st.button("Procesar Documento"):
            with st.spinner("Procesando documento..."):
                result = analyzer.process_document(text, doc_type)
                if result:
                    st.success("Documento procesado exitosamente")
    
    # Sección de Análisis
    st.header("Análisis de la Red")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estadísticas")
        stats = {
            "Total de Entidades": len(analyzer.entities),
            "Total de Relaciones": len(analyzer.relationships),
            "Funcionarios": len([e for e in analyzer.entities.values() if e['type'] == 'funcionario']),
            "Empresas": len([e for e in analyzer.entities.values() if e['type'] == 'empresa']),
            "Beneficiarios": len([e for e in analyzer.entities.values() if e['type'] == 'beneficiario']),
            "PPEs": len([e for e in analyzer.entities.values() if e['type'] == 'ppe'])
        }
        
        for key, value in stats.items():
            st.metric(key, value)
    
    with col2:
        st.subheader("Patrones Sospechosos")
        patterns = analyzer.detect_suspicious_patterns()
        for pattern in patterns:
            st.warning(
                f"**{pattern['type']}**\n\n"
                f"{pattern['description']}"
            )
    
    # Visualización de la red
    st.header("Visualización de la Red")
    fig = analyzer.generate_network_visualization()
    st.plotly_chart(fig, use_container_width=True)
    
    # Exportar resultados
    if st.button("Exportar Resultados"):
        results = {
            "timestamp": datetime.now().isoformat(),
            "entities": analyzer.entities,
            "relationships": analyzer.relationships,
            "suspicious_patterns": patterns,
            "statistics": stats
        }
        
        st.download_button(
            "Descargar JSON",
            data=json.dumps(results, indent=2, ensure_ascii=False),
            file_name="analisis_red_corrupcion.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()