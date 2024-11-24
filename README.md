
# LUPPA - Analizador de Redes de Corrupción

LUPPA es una herramienta de análisis basada en inteligencia artificial que permite detectar y visualizar redes de posibles vínculos corruptos entre funcionarios públicos, empresas contratistas, beneficiarios de programas y personas políticamente expuestas.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red.svg)](https://streamlit.io/)
[![Anthropic](https://img.shields.io/badge/Claude%20API-0.18.1-green.svg)](https://www.anthropic.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🔍 Características Principales

- **Procesamiento Inteligente de Documentos**: Análisis automatizado de documentos PDF y TXT utilizando la API de Claude para extraer entidades y relaciones relevantes.

- **Detección de Patrones Sospechosos**: 
  - Identificación de ciclos cerrados entre funcionarios y empresas
  - Detección de concentración anormal de contratos
  - Análisis de relaciones cruzadas y conflictos de interés

- **Visualización Interactiva**: 
  - Grafos interactivos de relaciones usando Plotly
  - Visualización por tipos de entidades
  - Exploración detallada de conexiones

- **Análisis Estadístico**: 
  - Métricas de red
  - Indicadores de riesgo
  - Patrones temporales

## 💻 Requisitos

- Python 3.8+
- API Key de Anthropic (Claude)
- Dependencias listadas en `requirements.txt`

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/holasoymalva/luppa.git
cd luppa
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar API Key:
- Crear archivo `.env` en el directorio raíz
- Agregar tu API Key de Anthropic:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## 🎯 Uso

1. Ejecutar la aplicación:
```bash
streamlit run app.py
```

2. Acceder a la interfaz web en `http://localhost:8501`

3. Cargar documentos:
   - Seleccionar tipo de documento
   - Subir archivo (PDF/TXT)
   - Procesar y visualizar resultados

## 🔧 Estructura del Proyecto

```
luppa/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── .env                  # Configuración (no incluido en repo)
├── assets/              # Recursos estáticos
├── docs/                # Documentación
└── tests/               # Tests unitarios
```

## 🎨 Visualizaciones

### Red de Relaciones
![Red de Relaciones](assets/network-example.png)

### Dashboard de Análisis
![Dashboard](assets/dashboard-example.png)

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] Implementación de análisis temporal
- [ ] Integración con bases de datos externas
- [ ] Mejoras en la visualización de subgrafos
- [ ] Sistema de alertas en tiempo real
- [ ] API REST para consultas externas

## 🔒 Seguridad

Este proyecto está diseñado para el análisis de información pública. Por favor:

- No subir información sensible o confidencial
- Mantener las API keys seguras
- Seguir las políticas de privacidad aplicables
- Reportar vulnerabilidades de seguridad

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙋 Soporte

Si tienes preguntas o necesitas ayuda:

- Abre un issue en GitHub
- Consulta la [documentación](docs/README.md)
- Contacta al equipo de desarrollo

## 🌟 Reconocimientos

- [Anthropic](https://www.anthropic.com/) por la API de Claude
- [Streamlit](https://streamlit.io/) por el framework de la interfaz
- [NetworkX](https://networkx.org/) por las herramientas de análisis de redes
- [Plotly](https://plotly.com/) por las visualizaciones interactivas

---
Desarrollado con ❤️ por el equipo de LUPPA