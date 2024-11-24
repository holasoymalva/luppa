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
import logging
from typing import Optional, Dict, List, Any

# Importar configuración
from config import config, DOCUMENT_TYPES, ENTITY_TYPES, RELATIONSHIP_TYPES

# Configurar logging
logging.basicConfig(
    level=config.app_config["log_level"],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CorruptionNetworkAnalyzer:
    def __init__(self):
        """Inicializa el analizador con la configuración de Anthropic"""
        try:
            self.client = anthropic.Client(config.anthropic_config["api_key"])
            self.graph = nx.Graph()
            self.entities = {}
            self.relationships = []
            logger.info("Analizador iniciado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el analizador: {str(e)}")
            raise
        
    def process_document(self, document_text: str, document_type: str) -> Optional[Dict]:
        """Procesa un documento usando Claude para extraer entidades y relaciones"""
        try:
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
            {
                "entities": [
                    {
                        "id": "string",
                        "name": "string",
                        "type": "funcionario|empresa|beneficiario|ppe",
                        "attributes": {}
                    }
                ],
                "relationships": [
                    {
                        "source": "entity_id",
                        "target": "entity_id",
                        "type": "familiar|comercial|politica|beneficio",
                        "attributes": {}
                    }
                ]
            }
            """
            
            response = self.client.messages.create(
                model=config.anthropic_config["model"],
                max_tokens=config.anthropic_config["max_tokens"],
                temperature=config.anthropic_config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content)
            self._update_graph(result)
            logger.info(f"Documento procesado exitosamente: {len(result['entities'])} entidades encontradas")
            return result
        except Exception as e:
            logger.error(f"Error procesando documento: {str(e)}")
            return None
    
    def _update_graph(self, analysis_result: Dict):
        """Actualiza el grafo con nuevas entidades y relaciones"""
        try:
            # Agregar entidades
            for entity in analysis_result['entities']:
                entity_config = config.get_entity_config(entity['type'])
                self.graph.add_node(
                    entity['id'],
                    **entity['attributes'],
                    node_type=entity['type'],
                    name=entity['name'],
                    color=entity_config['color'],
                    icon=entity_config['icon']
                )
                self.entities[entity['id']] = entity
                
            # Agregar relaciones
            for rel in analysis_result['relationships']:
                rel_config = config.get_relationship_config(rel['type'])
                self.graph.add_edge(
                    rel['source'],
                    rel['target'],
                    **rel['attributes'],
                    relationship_type=rel['type'],
                    color=rel_config['color'],
                    risk_factor=rel_config['risk_factor']
                )
                self.relationships.append(rel)
                
            logger.info("Grafo actualizado correctamente")
        except Exception as e:
            logger.error(f"Error actualizando el grafo: {str(e)}")
            raise
    
    def detect_suspicious_patterns(self) -> List[Dict]:
        """Detecta patrones sospechosos en la red"""
        suspicious_patterns = []
        
        try:
            # Detectar ciclos cerrados entre funcionarios y empresas
            cycles = nx.cycle_basis(self.graph)
            for cycle in cycles:
                if len(cycle) >= config.risk_thresholds["min_cycle_length"]:
                    cycle_types = [self.entities[node]['type'] for node in cycle]
                    if 'funcionario' in cycle_types and 'empresa' in cycle_types:
                        suspicious_patterns.append({
                            'type': 'ciclo_sospechoso',
                            'nodes': cycle,
                            'risk_level': 'high',
                            'description': 'Ciclo cerrado entre funcionarios y empresas'
                        })
            
            # Detectar concentración de contratos
            empresa_degrees = {
                node: degree for node, degree in self.graph.degree()
                if self.entities[node]['type'] == 'empresa'
            }
            if empresa_degrees:
                mean_degree = sum(empresa_degrees.values()) / len(empresa_degrees)
                std_degree = (
                    sum((d - mean_degree) ** 2 for d in empresa_degrees.values()) 
                    / len(empresa_degrees)
                ) ** 0.5
                
                threshold = mean_degree + (
                    config.risk_thresholds["max_degree_std"] * std_degree
                )
                
                for empresa, degree in empresa_degrees.items():
                    if degree > threshold:
                        suspicious_patterns.append({
                            'type': 'concentracion_contratos',
                            'node': empresa,
                            'degree': degree,
                            'risk_level': 'high',
                            'description': 'Concentración anormal de contratos'
                        })
            
            logger.info(f"Detección de patrones completada: {len(suspicious_patterns)} patrones encontrados")
            return suspicious_patterns
        except Exception as e:
            logger.error(f"Error detectando patrones sospechosos: {str(e)}")
            return []
    
    def generate_network_visualization(self) -> go.Figure:
        """Genera una visualización de la red usando Plotly"""
        try:
            pos = nx.spring_layout(self.graph)
            
            viz_config = config.viz_config
            
            # Configurar nodos
            node_trace = go.Scatter(
                x=[],
                y=[],
                text=[],
                mode='markers+text',
                hoverinfo='text',
                marker=dict(
                    size=viz_config["node_size"],
                    color=[],
                    colorscale='Viridis',
                    line_width=2))

            # Configurar enlaces
            edge_trace = go.Scatter(
                x=[],
                y=[],
                line=dict(width=viz_config["edge_width"], color='#888'),
                hoverinfo='none',
                mode='lines')

            # Agregar posiciones de nodos
            for node in self.graph.nodes():
                x, y = pos[node]
                node_trace['x'] += tuple([x])
                node_trace['y'] += tuple([y])
                node_info = self.entities[node]
                node_trace['text'] += tuple([
                    f"{node_info['name']}\n({ENTITY_TYPES[node_info['type']]['name']})"
                ])
                
                node_trace['marker']['color'] += tuple([
                    list(ENTITY_TYPES.keys()).index(node_info['type']) 
                    / len(ENTITY_TYPES)
                ])

            # Agregar enlaces
            for edge in self.graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])

            # Crear figura
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Red de Relaciones',
                    showlegend=False,
                    hovermode='closest',
                    margin=viz_config["margin"],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )
            
            logger.info("Visualización generada correctamente")
            return fig
        except Exception as e:
            logger.error(f"Error generando visualización: {str(e)}")
            raise

def main():
    try:
        st.set_page_config(
            page_title=config.app_config["name"],
            layout="wide"
        )
        
        st.title(config.app_config["name"])
        
        # Inicializar el analizador
        analyzer = CorruptionNetworkAnalyzer()
        
        # Sección de carga de documentos
        st.header("Carga de Documentos")
        
        doc_type = st.selectbox(
            "Tipo de Documento",
            options=list(DOCUMENT_TYPES.keys()),
            format_func=lambda x: DOCUMENT_TYPES[x]
        )
        
        uploaded_file = st.file_uploader(
            "Cargar documento",
            type=["txt", "pdf"]
        )
        
        if uploaded_file:
            try:
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
            except Exception as e:
                st.error(f"Error procesando archivo: {str(e)}")
        
        # Sección de Análisis
        st.header("Análisis de la Red")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Estadísticas")
            stats = {
                "Total de Entidades": len(analyzer.entities),
                "Total de Relaciones": len(analyzer.relationships),
                "Funcionarios": len([
                    e for e in analyzer.entities.values()
                    if e['type'] == 'funcionario'
                ]),
                "Empresas": len([
                    e for e in analyzer.entities.values()
                    if e['type'] == 'empresa'
                ]),
                "Beneficiarios": len([
                    e for e in analyzer.entities.values()
                    if e['type'] == 'beneficiario'
                ]),
                "PPEs": len([
                    e for e in analyzer.entities.values()
                    if e['type'] == 'ppe'
                ])
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
            
            # Guardar en directorio de exportaciones
            export_path = config.EXPORTS_DIR / f"analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Ofrecer descarga
            with open(export_path, 'r', encoding='utf-8') as f:
                st.download_button(
                    "Descargar JSON",
                    f.read(),
                    file_name="analisis_red_corrupcion.json",
                    mime="application/json"
                )
            
            st.success(f"Resultados exportados a: {export_path}")
            
    except Exception as e:
        logger.error(f"Error en la aplicación: {str(e)}")
        st.error("Ha ocurrido un error en la aplicación. Por favor, revisa los logs para más detalles.")

if __name__ == "__main__":
    if config.app_config["debug"]:
        # En modo debug, mostrar traceback completo
        main()
    else:
        # En producción, capturar errores
        try:
            main()
        except Exception as e:
            logger.error(f"Error fatal en la aplicación: {str(e)}")
            st.error("Ha ocurrido un error inesperado. Por favor, contacta al administrador.")