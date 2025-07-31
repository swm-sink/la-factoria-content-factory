"""
Lazy loading utilities for efficient data fetching.

This module provides lazy loading patterns to defer expensive operations until needed.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LazyLoader(Generic[T]):
    """Lazy loads data when first accessed."""
    
    def __init__(self, loader_func: Callable[[], Union[T, Callable[[], T]]]):
        """
        Initialize lazy loader.
        
        Args:
            loader_func: Function that loads the data when called
        """
        self._loader_func = loader_func
        self._loaded = False
        self._value: Optional[T] = None
        self._loading: Optional[asyncio.Task] = None
        
    async def get(self) -> T:
        """
        Get the value, loading it if necessary.
        
        Returns:
            The loaded value
        """
        if self._loaded:
            return self._value
            
        # Handle concurrent access
        if self._loading:
            return await self._loading
            
        # Start loading
        self._loading = asyncio.create_task(self._load())
        return await self._loading
        
    async def _load(self) -> T:
        """Load the value."""
        try:
            if asyncio.iscoroutinefunction(self._loader_func):
                self._value = await self._loader_func()
            else:
                self._value = self._loader_func()
                
            self._loaded = True
            return self._value
        finally:
            self._loading = None
            
    def is_loaded(self) -> bool:
        """Check if value is already loaded."""
        return self._loaded
        
    def reset(self):
        """Reset the loader, forcing a reload on next access."""
        self._loaded = False
        self._value = None
        self._loading = None


class LazyDict(Dict[str, LazyLoader[Any]]):
    """Dictionary with lazy-loaded values."""
    
    def __init__(self):
        super().__init__()
        self._loaders: Dict[str, LazyLoader] = {}
        
    def add_lazy(self, key: str, loader_func: Callable[[], Any]):
        """
        Add a lazy-loaded value.
        
        Args:
            key: Dictionary key
            loader_func: Function to load the value
        """
        self._loaders[key] = LazyLoader(loader_func)
        
    async def get_value(self, key: str) -> Any:
        """
        Get a value, loading it if necessary.
        
        Args:
            key: Dictionary key
            
        Returns:
            The value
        """
        if key not in self._loaders:
            raise KeyError(f"No lazy loader for key: {key}")
            
        return await self._loaders[key].get()
        
    async def load_all(self) -> Dict[str, Any]:
        """
        Load all lazy values.
        
        Returns:
            Dictionary with all loaded values
        """
        tasks = {key: loader.get() for key, loader in self._loaders.items()}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        loaded = {}
        for (key, _), result in zip(tasks.items(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to load lazy value for key '{key}': {result}")
            else:
                loaded[key] = result
                
        return loaded
        
    def is_loaded(self, key: str) -> bool:
        """Check if a value is already loaded."""
        return key in self._loaders and self._loaders[key].is_loaded()


class LazyRelationship:
    """Represents a lazy-loaded relationship between entities."""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        relationship_type: str,
        loader_func: Callable[[str, str], Any]
    ):
        """
        Initialize lazy relationship.
        
        Args:
            entity_type: Type of the parent entity
            entity_id: ID of the parent entity
            relationship_type: Type of relationship (e.g., 'jobs', 'users')
            loader_func: Function to load related data
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.relationship_type = relationship_type
        self._loader = LazyLoader(
            lambda: loader_func(entity_id, relationship_type)
        )
        
    async def load(self) -> Any:
        """Load the related data."""
        return await self._loader.get()
        
    def is_loaded(self) -> bool:
        """Check if relationship is already loaded."""
        return self._loader.is_loaded()


class EagerLoader:
    """Manages eager loading of related data to prevent N+1 queries."""
    
    def __init__(self):
        self._includes: Dict[str, Set[str]] = {}
        
    def include(self, entity_type: str, *relationships: str) -> 'EagerLoader':
        """
        Specify relationships to eager load.
        
        Args:
            entity_type: Type of entity
            relationships: Relationship names to load
            
        Returns:
            Self for chaining
        """
        if entity_type not in self._includes:
            self._includes[entity_type] = set()
            
        self._includes[entity_type].update(relationships)
        return self
        
    async def load_batch(
        self,
        entity_type: str,
        entity_ids: List[str],
        loader_func: Callable[[str, List[str], str], Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Load entities with their relationships in batch.
        
        Args:
            entity_type: Type of entities
            entity_ids: List of entity IDs
            loader_func: Function to load relationships
            
        Returns:
            Dictionary mapping entity ID to loaded data with relationships
        """
        relationships = self._includes.get(entity_type, set())
        if not relationships:
            # No relationships to load
            return {entity_id: {} for entity_id in entity_ids}
            
        # Load all relationships in parallel
        tasks = {}
        for relationship in relationships:
            tasks[relationship] = loader_func(entity_type, entity_ids, relationship)
            
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Organize results by entity ID
        loaded_data = {entity_id: {} for entity_id in entity_ids}
        
        for relationship, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to load relationship '{relationship}': {result}")
                continue
                
            # Assuming result is a dict mapping entity_id to relationship data
            for entity_id, rel_data in result.items():
                if entity_id in loaded_data:
                    loaded_data[entity_id][relationship] = rel_data
                    
        return loaded_data


# Global eager loader instance
_eager_loader: Optional[EagerLoader] = None


def get_eager_loader() -> EagerLoader:
    """Get or create global eager loader instance."""
    global _eager_loader
    if _eager_loader is None:
        _eager_loader = EagerLoader()
    return _eager_loader