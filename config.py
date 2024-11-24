# config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno desde .env
load_dotenv()

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = BASE_DIR / "temp"
EXPORTS_DIR = BASE_DIR / "exports"

# Configuración de la API de Anthropic
ANTHROPIC_CONFIG = {
    "api_key": os.getenv("ANTHROPIC_API_KEY"),
    "model": "claude-3-opus-20240229",
    "max_tokens": 4096,
    "temperature": 0.7
}

# Configuración de la aplicación
APP_CONFIG = {
    "name": "LUPPA - Analizador de Redes de Corrupción",
    "version": "1.0.0",
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO")
}

# Tipos de documentos soportados
DOCUMENT_TYPES = {
    "declaracion_patrimonial": "Declaración Patrimonial",
    "contrato_publico": "Contrato Público",
    "lista_beneficiarios": "Lista de Beneficiarios",
    "declaracion_intereses": "Declaración de Intereses",
    "otro": "Otro"
}

# Tipos de entidades y sus configuraciones
ENTITY_TYPES = {
    "funcionario": {
        "name": "Funcionario Público",
        "color": "#FF6B6B",
        "icon": "user"
    },
    "empresa": {
        "name": "Empresa Contratista",
        "color": "#4ECDC4",
        "icon": "building"
    },
    "beneficiario": {
        "name": "Beneficiario",
        "color": "#45B7D1",
        "icon": "user-check"
    },
    "ppe": {
        "name": "Persona Políticamente Expuesta",
        "color": "#96CEB4",
        "icon": "user-star"
    }
}

# Tipos de relaciones y sus atributos
RELATIONSHIP_TYPES = {
    "familiar": {
        "name": "Relación Familiar",
        "risk_factor": 0.8,
        "color": "#FF0000"
    },
    "comercial": {
        "name": "Relación Comercial",
        "risk_factor": 0.6,
        "color": "#00FF00"
    },
    "politica": {
        "name": "Relación Política",
        "risk_factor": 0.7,
        "color": "#0000FF"
    },
    "beneficio": {
        "name": "Beneficio Recibido",
        "risk_factor": 0.5,
        "color": "#FFFF00"
    }
}

# Umbrales para detección de patrones sospechosos
RISK_THRESHOLDS = {
    "high": 0.7,
    "medium": 0.4,
    "low": 0.2,
    "min_cycle_length": 3,
    "max_degree_std": 2.0
}

# Configuración de visualización
VISUALIZATION_CONFIG = {
    "node_size": 20,
    "edge_width": 0.5,
    "font_size": 10,
    "margin": dict(b=20, l=5, r=5, t=40)
}

class Config:
    """Clase para manejar la configuración de la aplicación"""
    
    def __init__(self):
        self._validate_config()
        self._create_directories()
        
    def _validate_config(self):
        """Valida la configuración necesaria"""
        if not ANTHROPIC_CONFIG["api_key"]:
            raise ValueError(
                "API Key de Anthropic no encontrada. "
                "Por favor, configura la variable de entorno ANTHROPIC_API_KEY"
            )
    
    def _create_directories(self):
        """Crea los directorios necesarios si no existen"""
        for directory in [TEMP_DIR, EXPORTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def anthropic_config(self) -> Dict[str, Any]:
        """Retorna la configuración de Anthropic"""
        return ANTHROPIC_CONFIG
    
    @property
    def app_config(self) -> Dict[str, Any]:
        """Retorna la configuración de la aplicación"""
        return APP_CONFIG
    
    def get_entity_config(self, entity_type: str) -> Dict[str, Any]:
        """Retorna la configuración para un tipo de entidad"""
        return ENTITY_TYPES.get(entity_type, ENTITY_TYPES["otro"])
    
    def get_relationship_config(self, relationship_type: str) -> Dict[str, Any]:
        """Retorna la configuración para un tipo de relación"""
        return RELATIONSHIP_TYPES.get(relationship_type, RELATIONSHIP_TYPES["otro"])
    
    @property
    def risk_thresholds(self) -> Dict[str, float]:
        """Retorna los umbrales de riesgo"""
        return RISK_THRESHOLDS
    
    @property
    def viz_config(self) -> Dict[str, Any]:
        """Retorna la configuración de visualización"""
        return VISUALIZATION_CONFIG

# Instancia global de configuración
config = Config()