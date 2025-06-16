from typing import Dict, List
from pydantic import RootModel, HttpUrl, BaseModel, Field
from pathlib import Path
from domain_config import (
    domain_manager, 
    get_document_categories, 
    get_entities,
    get_entity_urls,
    create_entity_enum,
    create_category_enum
)


def get_entity_enum():
    """Get the dynamic entity enum for the current domain"""
    return create_entity_enum()


def get_category_enum():
    """Get the dynamic document category enum for the current domain"""  
    return create_category_enum()


def get_entity_document_roots() -> Dict[str, List[HttpUrl]]:
    """Get document root URLs for all entities in the current domain"""
    entities = get_entities()
    result = {}
    
    for entity_id in entities.keys():
        urls = get_entity_urls(entity_id)
        if urls:
            result[entity_id] = [HttpUrl(url) for url in urls]
    
    return result


class GenericDocument(BaseModel):
    """Generic document model that works with any domain"""
    id: str = Field(..., description="Unique identifier for the document")
    entity: str = Field(..., description="Name of the entity (parent folder)")
    filename: str = Field(..., description="Name of the PDF file")
    path: str = Field(..., description="Full path to the PDF file")
    page: int = Field(..., description="Page number within the PDF")
    content: str = Field(..., description="Text content of the page")
    embedding: list[float] | None = Field(
        default=None,
        description="Embedding vector for the page content",
    )
    # DocumentAnalysis metadata fields
    retrieved_from: str | None = Field(default=None, description="URL from which the document was retrieved")
    retrieved_at: str | None = Field(default=None, description="ISO timestamp of when the document was retrieved")
    retrieved_etag: str | None = Field(default=None, description="ETag of the document at the time of retrieval")
    bank: str | None = Field(default=None, description="Bank name from DocumentAnalysis")
    content_hash: str | None = Field(default=None, description="Hash of the source file for integrity checks")
    category: str | None = Field(default=None, description="Document category")
    document_title: str | None = Field(default=None, description="Title of the document")
    effective_date: str | None = Field(default=None, description="ISO date when the document becomes effective")


# Helper functions for backward compatibility and easy migration
def initialize_domain(config_path: Path) -> None:
    """Initialize the domain with a specific configuration file"""
    domain_manager.load_config(config_path)


def get_current_entities() -> Dict[str, str]:
    """Get current entities as a simple dict mapping"""
    entities = get_entities()
    return {k: v.get('name', k) for k, v in entities.items()}


def get_current_categories() -> Dict[str, str]:
    """Get current document categories"""
    return get_document_categories()


def get_current_entity_urls() -> Dict[str, List[str]]:
    """Get current entity URLs"""
    entities = get_entities()
    result = {}
    
    for entity_id in entities.keys():
        urls = get_entity_urls(entity_id)
        if urls:
            result[entity_id] = urls
    
    return result


# Backward compatibility - these will be populated at runtime
class DynamicEntity:
    """Placeholder for dynamic entity enum"""
    pass


class DynamicDocumentCategory:
    """Placeholder for dynamic document category enum"""
    pass


# Functions to replace the old hardcoded enums
def Entity():
    """Get the current entity enum"""
    return get_entity_enum()


def DocumentCategory():
    """Get the current document category enum"""
    return get_category_enum()


def Categories():
    """Get the current categories dictionary"""
    return get_current_categories()


def EntityDocumentRoots():
    """Get the current entity document roots"""
    return get_entity_document_roots()