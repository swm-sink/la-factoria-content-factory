from ..services.cache import ContentCache
from ..services.tracker import ProgressTracker
from ..services.multistep import MultiStepContentGenerationService
from ..core.settings import settings

# Singleton cache for demo/dev; use proper DI in prod
_cache = ContentCache(settings.REDIS_URL)
_tracker = ProgressTracker(_cache.redis)
_multistep = MultiStepContentGenerationService()

def get_cache():
    return _cache

def get_tracker():
    return _tracker

def get_multistep():
    return _multistep 