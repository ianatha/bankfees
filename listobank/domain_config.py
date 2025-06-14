from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from pathlib import Path
import json


class DomainConfig(BaseModel):
    """Configuration for a specific domain (e.g., banking, insurance, retail)"""
    
    name: str = Field(..., description="Name of the domain (e.g., 'banking', 'insurance')")
    description: str = Field(..., description="Description of the domain")
    
    # Entity configuration (replaces hardcoded banks)
    entities: Dict[str, Dict[str, Any]] = Field(
        ..., 
        description="Map of entity identifiers to their configuration"
    )
    
    # Document categories for this domain
    document_categories: Dict[str, str] = Field(
        ...,
        description="Map of category identifiers to their descriptions"
    )
    
    # URL roots for document retrieval
    entity_urls: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of entity identifiers to their document root URLs"
    )
    
    # Default uncategorized category name
    default_category: str = Field(
        default="Uncategorized",
        description="Default category for uncategorized documents"
    )


class GenericEntity(str, Enum):
    """Dynamic enum that will be populated from config"""
    pass


class GenericDocumentCategory(str, Enum):
    """Dynamic enum that will be populated from config"""
    pass


class DomainManager:
    """Manages domain configurations and provides runtime access to domain-specific data"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("domain_config.json")
        self.config: Optional[DomainConfig] = None
        self._entity_enum = None
        self._category_enum = None
        
        if self.config_path.exists():
            self.load_config()
    
    def load_config(self, config_path: Optional[Path] = None) -> None:
        """Load domain configuration from JSON file"""
        if config_path:
            self.config_path = config_path
            
        if not self.config_path.exists():
            raise FileNotFoundError(f"Domain config file not found: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.config = DomainConfig(**config_data)
            
        # Reset cached enums
        self._entity_enum = None
        self._category_enum = None
    
    def save_config(self, config: DomainConfig, config_path: Optional[Path] = None) -> None:
        """Save domain configuration to JSON file"""
        if config_path:
            self.config_path = config_path
            
        self.config = config
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
    
    def get_entities(self) -> Dict[str, Any]:
        """Get all entities in the current domain"""
        if not self.config:
            raise ValueError("No domain configuration loaded")
        return self.config.entities
    
    def get_entity_config(self, entity_id: str) -> Dict[str, Any]:
        """Get configuration for a specific entity"""
        entities = self.get_entities()
        if entity_id not in entities:
            raise ValueError(f"Entity '{entity_id}' not found in domain configuration")
        return entities[entity_id]
    
    def get_document_categories(self) -> Dict[str, str]:
        """Get all document categories for the current domain"""
        if not self.config:
            raise ValueError("No domain configuration loaded")
        return self.config.document_categories
    
    def get_entity_urls(self, entity_id: str) -> List[str]:
        """Get URLs for a specific entity"""
        if not self.config:
            raise ValueError("No domain configuration loaded")
        return self.config.entity_urls.get(entity_id, [])
    
    def get_default_category(self) -> str:
        """Get the default category for uncategorized documents"""
        if not self.config:
            raise ValueError("No domain configuration loaded")
        return self.config.default_category
    
    def create_entity_enum(self) -> type:
        """Create a dynamic enum class for entities"""
        if self._entity_enum is None:
            if not self.config:
                raise ValueError("No domain configuration loaded")
                
            entity_dict = {k.upper(): k for k in self.config.entities.keys()}
            self._entity_enum = Enum('DynamicEntity', entity_dict)
        
        return self._entity_enum
    
    def create_category_enum(self) -> type:
        """Create a dynamic enum class for document categories"""
        if self._category_enum is None:
            if not self.config:
                raise ValueError("No domain configuration loaded")
                
            # Include default category
            categories = dict(self.config.document_categories)
            if self.config.default_category not in categories:
                categories[self.config.default_category] = "Uncategorized documents"
                
            category_dict = {k: k for k in categories.keys()}
            self._category_enum = Enum('DynamicDocumentCategory', category_dict)
        
        return self._category_enum


# Global domain manager instance
domain_manager = DomainManager()


def get_current_domain() -> DomainConfig:
    """Get the currently loaded domain configuration"""
    if not domain_manager.config:
        raise ValueError("No domain configuration loaded. Call load_domain_config() first.")
    return domain_manager.config


def load_domain_config(config_path: Path) -> None:
    """Load a domain configuration file"""
    domain_manager.load_config(config_path)


def get_entities() -> Dict[str, Any]:
    """Get all entities in the current domain"""
    return domain_manager.get_entities()


def get_entity_config(entity_id: str) -> Dict[str, Any]:
    """Get configuration for a specific entity"""
    return domain_manager.get_entity_config(entity_id)


def get_document_categories() -> Dict[str, str]:
    """Get all document categories for the current domain"""
    return domain_manager.get_document_categories()


def get_entity_urls(entity_id: str) -> List[str]:
    """Get URLs for a specific entity"""
    return domain_manager.get_entity_urls(entity_id)


def create_entity_enum() -> type:
    """Create a dynamic enum class for entities in the current domain"""
    return domain_manager.create_entity_enum()


def create_category_enum() -> type:
    """Create a dynamic enum class for document categories in the current domain"""
    return domain_manager.create_category_enum()