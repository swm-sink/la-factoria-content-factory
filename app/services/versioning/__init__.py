"""
Content versioning service package.

This package provides comprehensive content versioning functionality including:
- Version management with semantic versioning
- Content diffing and comparison
- Branch and merge support
- Content locking for concurrent edit prevention
"""

from .branch_manager import BranchManager
from .diff_engine import DiffEngine
from .merge_engine import MergeEngine
from .version_manager import VersionManager

__all__ = ["VersionManager", "DiffEngine", "MergeEngine", "BranchManager"]
