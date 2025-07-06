"""
Configuration Management Module - Handles application settings and API keys
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """Configuration for API keys and endpoints"""
    serpapi_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    arxiv_api_key: Optional[str] = None
    pubmed_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp"
    
    def __post_init__(self):
        """Load API keys from environment variables if not provided"""
        if not self.serpapi_key:
            self.serpapi_key = os.getenv("SERPAPI_KEY")
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.arxiv_api_key:
            self.arxiv_api_key = os.getenv("ARXIV_API_KEY")
        if not self.pubmed_api_key:
            self.pubmed_api_key = os.getenv("PUBMED_API_KEY")
        if not self.pinecone_api_key:
            self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not self.pinecone_environment:
            self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    
    def validate(self) -> Dict[str, bool]:
        """Validate API key availability"""
        return {
            "serpapi": bool(self.serpapi_key),
            "openai": bool(self.openai_api_key),
            "arxiv": bool(self.arxiv_api_key),
            "pubmed": bool(self.pubmed_api_key),
            "pinecone": bool(self.pinecone_api_key)
        }
    
    def get_required_keys(self) -> Dict[str, bool]:
        """Get status of required API keys"""
        return {
            "serpapi": bool(self.serpapi_key),
            "openai": bool(self.openai_api_key)
        }
    
    def get_optional_keys(self) -> Dict[str, bool]:
        """Get status of optional API keys"""
        return {
            "arxiv": bool(self.arxiv_api_key),
            "pubmed": bool(self.pubmed_api_key),
            "pinecone": bool(self.pinecone_api_key)
        }

@dataclass
class ResearchConfig:
    """Configuration for research parameters"""
    max_results_per_source: int = 10
    include_academic_sources: bool = True
    include_news_sources: bool = True
    include_web_sources: bool = True
    confidence_threshold: float = 0.7
    max_research_time: int = 300  # seconds
    parallel_research: bool = True
    max_sections: int = 10
    
    def validate(self) -> bool:
        """Validate research configuration"""
        return (
            1 <= self.max_results_per_source <= 50 and
            0.0 <= self.confidence_threshold <= 1.0 and
            self.max_research_time > 0 and
            self.max_sections > 0
        )

@dataclass
class MemoryConfig:
    """Configuration for memory management"""
    short_term_max_messages: int = 20
    short_term_max_age_hours: int = 24
    long_term_vector_store: str = "chroma"  # chroma, faiss, pinecone, memory
    long_term_collection_name: str = "research_memory"
    long_term_persist_directory: str = "./memory_db"
    auto_save_important_memories: bool = True
    importance_threshold: float = 0.8
    
    def validate(self) -> bool:
        """Validate memory configuration"""
        valid_stores = ["chroma", "faiss", "pinecone", "memory"]
        return (
            self.short_term_max_messages > 0 and
            self.short_term_max_age_hours > 0 and
            self.long_term_vector_store in valid_stores and
            0.0 <= self.importance_threshold <= 1.0
        )

@dataclass
class LoggingConfig:
    """Configuration for logging and chain-of-thought"""
    log_level: str = "INFO"
    log_file: str = "logs/chain_of_thought.json"
    max_log_entries: int = 1000
    auto_save_logs: bool = True
    include_tool_calls: bool = True
    include_timestamps: bool = True
    
    def validate(self) -> bool:
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        return (
            self.log_level in valid_levels and
            self.max_log_entries > 0
        )

@dataclass
class UIConfig:
    """Configuration for user interface"""
    page_title: str = "Deep Research Agent"
    layout: str = "wide"
    theme: str = "light"  # light, dark, auto
    show_chain_of_thought: bool = True
    show_memory_panel: bool = True
    show_detailed_logs: bool = True
    chat_history_limit: int = 50
    
    def validate(self) -> bool:
        """Validate UI configuration"""
        valid_layouts = ["centered", "wide"]
        valid_themes = ["light", "dark", "auto"]
        return (
            self.layout in valid_layouts and
            self.theme in valid_themes and
            self.chat_history_limit > 0
        )

class ConfigManager:
    """Main configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.api_config = APIConfig()
        self.research_config = ResearchConfig()
        self.memory_config = MemoryConfig()
        self.logging_config = LoggingConfig()
        self.ui_config = UIConfig()
        
        # Load configuration if file exists
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Load each configuration section
            if "api" in config_data:
                self.api_config = APIConfig(**config_data["api"])
            
            if "research" in config_data:
                self.research_config = ResearchConfig(**config_data["research"])
            
            if "memory" in config_data:
                self.memory_config = MemoryConfig(**config_data["memory"])
            
            if "logging" in config_data:
                self.logging_config = LoggingConfig(**config_data["logging"])
            
            if "ui" in config_data:
                self.ui_config = UIConfig(**config_data["ui"])
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                "api": asdict(self.api_config),
                "research": asdict(self.research_config),
                "memory": asdict(self.memory_config),
                "logging": asdict(self.logging_config),
                "ui": asdict(self.ui_config)
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def validate_all(self) -> Dict[str, bool]:
        """Validate all configuration sections"""
        return {
            "api": bool(self.api_config.validate()),
            "research": self.research_config.validate(),
            "memory": self.memory_config.validate(),
            "logging": self.logging_config.validate(),
            "ui": self.ui_config.validate()
        }
    
    def get_api_status(self) -> Dict[str, str]:
        """Get API status with user-friendly messages"""
        validation = self.api_config.validate()
        required = self.api_config.get_required_keys()
        
        status = {}
        
        # Required APIs
        status["SerpAPI"] = "✅ Ready" if required["serpapi"] else "❌ Required"
        status["OpenAI"] = "✅ Ready" if required["openai"] else "❌ Required"
        
        # Optional APIs
        status["ArXiv"] = "✅ Ready" if validation["arxiv"] else "⚠️ Optional"
        status["PubMed"] = "✅ Ready" if validation["pubmed"] else "⚠️ Optional"
        status["Pinecone"] = "✅ Ready" if validation["pinecone"] else "⚠️ Optional"
        
        return status
    
    def is_ready_for_research(self) -> bool:
        """Check if minimum requirements are met for research"""
        required = self.api_config.get_required_keys()
        return all(required.values())
    
    def get_missing_requirements(self) -> List[str]:
        """Get list of missing required configurations"""
        missing = []
        
        required = self.api_config.get_required_keys()
        for api, available in required.items():
            if not available:
                missing.append(f"{api.upper()} API key")
        
        if not self.research_config.validate():
            missing.append("Research configuration")
        
        if not self.memory_config.validate():
            missing.append("Memory configuration")
        
        return missing
    
    def update_api_config(self, **kwargs) -> None:
        """Update API configuration"""
        for key, value in kwargs.items():
            if hasattr(self.api_config, key):
                setattr(self.api_config, key, value)
    
    def update_research_config(self, **kwargs) -> None:
        """Update research configuration"""
        for key, value in kwargs.items():
            if hasattr(self.research_config, key):
                setattr(self.research_config, key, value)
    
    def update_memory_config(self, **kwargs) -> None:
        """Update memory configuration"""
        for key, value in kwargs.items():
            if hasattr(self.memory_config, key):
                setattr(self.memory_config, key, value)
    
    def update_logging_config(self, **kwargs) -> None:
        """Update logging configuration"""
        for key, value in kwargs.items():
            if hasattr(self.logging_config, key):
                setattr(self.logging_config, key, value)
    
    def update_ui_config(self, **kwargs) -> None:
        """Update UI configuration"""
        for key, value in kwargs.items():
            if hasattr(self.ui_config, key):
                setattr(self.ui_config, key, value)
    
    def reset_to_defaults(self) -> None:
        """Reset all configurations to defaults"""
        self.api_config = APIConfig()
        self.research_config = ResearchConfig()
        self.memory_config = MemoryConfig()
        self.logging_config = LoggingConfig()
        self.ui_config = UIConfig()
    
    def export_config(self, file_path: str) -> bool:
        """Export configuration to a different file"""
        try:
            config_data = {
                "api": asdict(self.api_config),
                "research": asdict(self.research_config),
                "memory": asdict(self.memory_config),
                "logging": asdict(self.logging_config),
                "ui": asdict(self.ui_config),
                "exported_at": "2024-01-01T00:00:00"  # Would use actual timestamp
            }
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Import configuration from a file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate and load each section
            if "api" in config_data:
                self.api_config = APIConfig(**config_data["api"])
            
            if "research" in config_data:
                self.research_config = ResearchConfig(**config_data["research"])
            
            if "memory" in config_data:
                self.memory_config = MemoryConfig(**config_data["memory"])
            
            if "logging" in config_data:
                self.logging_config = LoggingConfig(**config_data["logging"])
            
            if "ui" in config_data:
                self.ui_config = UIConfig(**config_data["ui"])
            
            return True
            
        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False

# Global configuration instance
_global_config = None

def get_config() -> ConfigManager:
    """Get or create global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config

def load_config_from_file(file_path: str) -> ConfigManager:
    """Load configuration from specific file"""
    return ConfigManager(file_path) 