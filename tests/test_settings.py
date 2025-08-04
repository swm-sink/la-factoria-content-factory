"""
Mock settings for testing quality assessment
"""

class MockSettings:
    QUALITY_THRESHOLD_OVERALL = 0.70
    QUALITY_THRESHOLD_EDUCATIONAL = 0.75
    QUALITY_THRESHOLD_FACTUAL = 0.85

# Replace the actual settings import for testing
import sys
sys.modules['src.core.config'] = type('MockModule', (), {'settings': MockSettings()})
