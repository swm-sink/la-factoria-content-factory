# ElevenLabs Text-to-Speech Integration Context

## Platform Overview

### Core Capabilities
- **Text-to-Speech**: High-quality voice synthesis across 70+ languages
- **Speech-to-Text**: Transcription services for audio content
- **Voice Cloning**: Create custom voices from audio samples
- **Voice Design**: Design synthetic voices with specific characteristics
- **Sound Effects**: Generate audio effects and ambient sounds
- **Multi-speaker Dialogue**: Natural conversations between different voices

## Model Selection for Educational Content

### 1. Eleven v3 (Alpha) - Premium Quality
```python
ELEVEN_V3_CONFIG = {
    "model_id": "eleven_flash_v2_5",
    "features": {
        "emotional_expressiveness": "highest",
        "languages": 70,
        "character_limit": 10000,
        "multi_speaker": True,
        "latency": "standard"
    },
    "use_cases": [
        "High-quality educational podcasts",
        "Emotional storytelling content",
        "Multi-character educational scenarios",
        "Premium audio content"
    ],
    "pricing": "highest_tier"
}
```

### 2. Eleven Flash v2.5 - Low Latency
```python
ELEVEN_FLASH_CONFIG = {
    "model_id": "eleven_flash_v2_5", 
    "features": {
        "latency": "~75ms",
        "languages": 32,
        "character_limit": 40000,
        "cost_efficiency": "50% lower cost",
        "streaming": True
    },
    "use_cases": [
        "Real-time content generation",
        "Interactive educational tools",
        "Live tutoring applications",
        "Quick content previews"
    ],
    "pricing": "cost_optimized"
}
```

### 3. Eleven Multilingual v2 - Stable Production
```python
ELEVEN_MULTILINGUAL_CONFIG = {
    "model_id": "eleven_multilingual_v2",
    "features": {
        "consistency": "high",
        "languages": 29,
        "stability": "production_ready",
        "long_form": True
    },
    "use_cases": [
        "Consistent educational series",
        "Long-form study guides",
        "Standardized pronunciation",
        "Multilingual content"
    ],
    "pricing": "balanced"
}
```

## Integration Patterns for La Factoria

### 1. Basic Text-to-Speech Implementation
```python
import requests
import os
from typing import Dict, Optional, List
import asyncio
import aiohttp

class ElevenLabsService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice
        model_id: str = "eleven_flash_v2_5",
        voice_settings: Optional[Dict] = None
    ) -> bytes:
        """Generate speech from text asynchronously."""
        
        if not voice_settings:
            voice_settings = {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error: {response.status} - {error_text}")

    async def generate_educational_podcast(
        self,
        script_segments: List[Dict],
        output_file: str = "educational_podcast.mp3"
    ) -> str:
        """Generate multi-speaker educational podcast."""
        
        audio_segments = []
        
        for segment in script_segments:
            speaker = segment.get("speaker", "host")
            text = segment.get("text", "")
            voice_id = self._get_voice_for_speaker(speaker)
            
            # Generate audio for this segment
            audio_data = await self.generate_speech(
                text=text,
                voice_id=voice_id,
                model_id="eleven_flash_v2_5"  # Fast for interactive content
            )
            
            audio_segments.append(audio_data)
        
        # Combine audio segments (would use audio processing library)
        combined_audio = self._combine_audio_segments(audio_segments)
        
        # Save to file
        with open(output_file, "wb") as f:
            f.write(combined_audio)
        
        return output_file
    
    def _get_voice_for_speaker(self, speaker: str) -> str:
        """Map speaker roles to voice IDs."""
        voice_mapping = {
            "host": "21m00Tcm4TlvDq8ikWAM",      # Rachel - Professional
            "expert": "AZnzlk1XvdvUeBnXmlld",    # Domi - Knowledgeable
            "student": "EXAVITQu4vr4xnSDxMaL",   # Sarah - Curious
            "narrator": "ErXwobaYiN019PkySvjV"   # Antoni - Clear
        }
        return voice_mapping.get(speaker, voice_mapping["host"])
    
    def _combine_audio_segments(self, segments: List[bytes]) -> bytes:
        """Combine multiple audio segments into one file."""
        # This would use a library like pydub
        # For now, just concatenate (not ideal for production)
        return b"".join(segments)
```

### 2. Advanced Streaming Implementation
```python
import websockets
import json
import base64

class ElevenLabsStreamingService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.websocket_url = "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    
    async def stream_speech(
        self,
        text_generator,  # Async generator yielding text chunks
        voice_id: str,
        on_audio_chunk=None
    ):
        """Stream audio generation for real-time content."""
        
        uri = self.websocket_url.format(voice_id=voice_id)
        
        async with websockets.connect(
            uri,
            extra_headers={"xi-api-key": self.api_key}
        ) as websocket:
            
            # Send initial configuration
            config = {
                "text": " ",
                "voice_settings": {
                    "stability": 0.8,
                    "similarity_boost": 0.75
                },
                "generation_config": {
                    "chunk_length_schedule": [120, 160, 250, 290]
                }
            }
            
            await websocket.send(json.dumps(config))
            
            # Stream text and receive audio
            async for text_chunk in text_generator:
                # Send text chunk
                message = {
                    "text": text_chunk,
                    "try_trigger_generation": True
                }
                await websocket.send(json.dumps(message))
                
                # Receive and process audio chunks
                try:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if "audio" in data:
                        audio_chunk = base64.b64decode(data["audio"])
                        if on_audio_chunk:
                            await on_audio_chunk(audio_chunk)
                            
                except websockets.exceptions.ConnectionClosed:
                    break
            
            # Send end marker
            await websocket.send(json.dumps({"text": ""}))

async def stream_educational_content(content_generator, voice_id):
    """Example usage of streaming for educational content."""
    
    streaming_service = ElevenLabsStreamingService(api_key=os.environ["ELEVENLABS_API_KEY"])
    
    audio_chunks = []
    
    async def collect_audio(chunk):
        audio_chunks.append(chunk)
    
    await streaming_service.stream_speech(
        content_generator,
        voice_id,
        on_audio_chunk=collect_audio
    )
    
    return b"".join(audio_chunks)
```

### 3. Voice Management for Educational Content
```python
class EducationalVoiceManager:
    def __init__(self, elevenlabs_service: ElevenLabsService):
        self.service = elevenlabs_service
        self.educational_voices = self._setup_educational_voices()
    
    def _setup_educational_voices(self) -> Dict:
        """Define voices optimized for educational content."""
        return {
            "elementary": {
                "primary": "EXAVITQu4vr4xnSDxMaL",  # Sarah - Friendly, clear
                "characteristics": "Warm, encouraging, slow pace",
                "settings": {
                    "stability": 0.85,
                    "similarity_boost": 0.8,
                    "style": 0.3,  # Less dramatic
                    "use_speaker_boost": True
                }
            },
            "middle_school": {
                "primary": "21m00Tcm4TlvDq8ikWAM",  # Rachel - Professional
                "characteristics": "Clear, engaging, moderate pace",
                "settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            },
            "high_school": {
                "primary": "ErXwobaYiN019PkySvjV",  # Antoni - Authoritative
                "characteristics": "Professional, clear, natural pace",
                "settings": {
                    "stability": 0.7,
                    "similarity_boost": 0.7,
                    "style": 0.6,
                    "use_speaker_boost": True
                }
            },
            "college": {
                "primary": "AZnzlk1XvdvUeBnXmlld",  # Domi - Sophisticated
                "characteristics": "Academic, precise, efficient pace",
                "settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.65,
                    "style": 0.7,
                    "use_speaker_boost": True
                }
            }
        }
    
    async def generate_for_audience(
        self,
        text: str,
        audience_level: str,
        content_type: str = "explanation"
    ) -> bytes:
        """Generate audio optimized for specific audience and content type."""
        
        voice_config = self.educational_voices.get(audience_level, self.educational_voices["high_school"])
        
        # Adjust settings based on content type
        settings = voice_config["settings"].copy()
        
        if content_type == "story":
            settings["style"] = min(settings["style"] + 0.2, 1.0)  # More expressive
        elif content_type == "instruction":
            settings["stability"] = min(settings["stability"] + 0.1, 1.0)  # More stable
        elif content_type == "question":
            settings["style"] = max(settings["style"] - 0.1, 0.0)  # Less dramatic
        
        return await self.service.generate_speech(
            text=text,
            voice_id=voice_config["primary"],
            voice_settings=settings
        )
    
    async def create_dialogue(
        self,
        dialogue_segments: List[Dict],
        audience_level: str
    ) -> bytes:
        """Create educational dialogue with multiple speakers."""
        
        audio_segments = []
        
        for segment in dialogue_segments:
            speaker_role = segment.get("role", "teacher")
            text = segment.get("text", "")
            
            # Select appropriate voice for role and audience
            if speaker_role == "teacher":
                voice_id = self.educational_voices[audience_level]["primary"]
                settings = self.educational_voices[audience_level]["settings"]
            elif speaker_role == "student":
                # Use a different voice for student questions
                voice_id = "EXAVITQu4vr4xnSDxMaL"  # Sarah for student
                settings = {
                    "stability": 0.8,
                    "similarity_boost": 0.75,
                    "style": 0.4,
                    "use_speaker_boost": True
                }
            else:
                voice_id = self.educational_voices[audience_level]["primary"]
                settings = self.educational_voices[audience_level]["settings"]
            
            audio_data = await self.service.generate_speech(
                text=text,
                voice_id=voice_id,
                voice_settings=settings
            )
            
            audio_segments.append(audio_data)
            
            # Add brief pause between speakers
            if len(audio_segments) > 0:
                pause_audio = self._generate_silence(duration=0.5)  # 0.5 second pause
                audio_segments.append(pause_audio)
        
        return self.service._combine_audio_segments(audio_segments)
    
    def _generate_silence(self, duration: float) -> bytes:
        """Generate silence audio data."""
        # This would generate actual silence audio data
        # For now, return empty bytes (placeholder)
        return b""
```

## Cost Optimization Strategies

### 1. Character Optimization
```python
class CostOptimizedTTS:
    def __init__(self, elevenlabs_service: ElevenLabsService):
        self.service = elevenlabs_service
        self.pricing = {
            "eleven_flash_v2_5": 0.0003,  # per character (example)
            "eleven_multilingual_v2": 0.0006,
            "eleven_v3": 0.0012
        }
    
    def optimize_text_for_tts(self, text: str) -> str:
        """Optimize text to reduce character count while maintaining clarity."""
        
        optimizations = [
            # Remove extra whitespace
            lambda t: re.sub(r'\s+', ' ', t.strip()),
            
            # Replace common long phrases with shorter equivalents
            lambda t: t.replace('in other words', 'i.e.'),
            lambda t: t.replace('for example', 'e.g.'),
            lambda t: t.replace('that is to say', 'namely'),
            
            # Remove unnecessary filler words for TTS
            lambda t: re.sub(r'\b(um|uh|well|you know)\b', '', t, flags=re.IGNORECASE),
            
            # Convert numbers to more TTS-friendly format
            lambda t: re.sub(r'\b(\d+)%\b', r'\1 percent', t),
            lambda t: re.sub(r'\$(\d+)\b', r'\1 dollars', t),
        ]
        
        optimized_text = text
        for optimization in optimizations:
            optimized_text = optimization(optimized_text)
        
        return optimized_text
    
    def estimate_cost(self, text: str, model_id: str) -> float:
        """Estimate TTS generation cost."""
        character_count = len(text)
        price_per_char = self.pricing.get(model_id, self.pricing["eleven_multilingual_v2"])
        return character_count * price_per_char
    
    async def generate_cost_optimized(
        self,
        text: str,
        max_budget: float,
        audience_level: str = "high_school"
    ) -> Dict:
        """Generate audio within budget constraints."""
        
        # Optimize text first
        optimized_text = self.optimize_text_for_tts(text)
        
        # Choose most cost-effective model within budget
        for model_id in ["eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3"]:
            estimated_cost = self.estimate_cost(optimized_text, model_id)
            
            if estimated_cost <= max_budget:
                voice_manager = EducationalVoiceManager(self.service)
                audio_data = await voice_manager.generate_for_audience(
                    optimized_text,
                    audience_level
                )
                
                return {
                    "audio_data": audio_data,
                    "model_used": model_id,
                    "estimated_cost": estimated_cost,
                    "character_count": len(optimized_text),
                    "optimization_savings": len(text) - len(optimized_text)
                }
        
        raise ValueError(f"Cannot generate audio within budget of ${max_budget}")
```

### 2. Caching Strategy
```python
import hashlib
import json
from pathlib import Path

class TTSCacheManager:
    def __init__(self, cache_dir: str = "./tts_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, text: str, voice_id: str, settings: Dict) -> str:
        """Generate unique cache key for TTS request."""
        content = f"{text}|{voice_id}|{json.dumps(settings, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """Retrieve cached audio if available."""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        if cache_file.exists():
            with open(cache_file, "rb") as f:
                return f.read()
        
        return None
    
    async def cache_audio(self, cache_key: str, audio_data: bytes) -> None:
        """Cache generated audio for reuse."""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        with open(cache_file, "wb") as f:
            f.write(audio_data)
    
    async def generate_with_cache(
        self,
        service: ElevenLabsService,
        text: str,
        voice_id: str,
        voice_settings: Dict
    ) -> bytes:
        """Generate audio with caching to avoid duplicate API calls."""
        
        cache_key = self.get_cache_key(text, voice_id, voice_settings)
        
        # Try to get from cache first
        cached_audio = await self.get_cached_audio(cache_key)
        if cached_audio:
            return cached_audio
        
        # Generate new audio
        audio_data = await service.generate_speech(
            text=text,
            voice_id=voice_id,
            voice_settings=voice_settings
        )
        
        # Cache for future use
        await self.cache_audio(cache_key, audio_data)
        
        return audio_data
```

## Production Integration Patterns

### 1. FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    audience_level: str = "high_school"
    content_type: str = "explanation"
    voice_preference: Optional[str] = None

class TTSResponse(BaseModel):
    audio_url: str
    duration_seconds: float
    character_count: int
    estimated_cost: float

@app.post("/api/v1/tts/generate", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Generate text-to-speech audio for educational content."""
    
    try:
        # Initialize services
        elevenlabs_service = ElevenLabsService(api_key=os.environ["ELEVENLABS_API_KEY"])
        voice_manager = EducationalVoiceManager(elevenlabs_service)
        cache_manager = TTSCacheManager()
        
        # Generate audio with caching
        audio_data = await cache_manager.generate_with_cache(
            service=elevenlabs_service,
            text=request.text,
            voice_id=voice_manager.educational_voices[request.audience_level]["primary"],
            voice_settings=voice_manager.educational_voices[request.audience_level]["settings"]
        )
        
        # Save to storage and get URL
        audio_filename = f"tts_{current_user.id}_{uuid.uuid4().hex}.mp3"
        audio_url = await save_audio_to_storage(audio_data, audio_filename)
        
        # Calculate metrics
        duration = estimate_audio_duration(audio_data)
        cost = CostOptimizedTTS(elevenlabs_service).estimate_cost(request.text, "eleven_flash_v2_5")
        
        # Track usage
        background_tasks.add_task(
            log_tts_usage,
            user_id=current_user.id,
            character_count=len(request.text),
            cost=cost
        )
        
        return TTSResponse(
            audio_url=audio_url,
            duration_seconds=duration,
            character_count=len(request.text),
            estimated_cost=cost
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
```

### 2. Error Handling and Fallbacks
```python
class RobustTTSService:
    def __init__(self):
        self.primary_service = ElevenLabsService(api_key=os.environ["ELEVENLABS_API_KEY"])
        self.fallback_services = []  # Could include other TTS providers
    
    async def generate_with_fallback(
        self,
        text: str,
        voice_config: Dict,
        max_retries: int = 3
    ) -> bytes:
        """Generate TTS with automatic fallbacks and retries."""
        
        last_error = None
        
        # Try primary service first
        for attempt in range(max_retries):
            try:
                return await self.primary_service.generate_speech(
                    text=text,
                    voice_id=voice_config["voice_id"],
                    voice_settings=voice_config["settings"]
                )
            except Exception as e:
                last_error = e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Try fallback services
        for fallback_service in self.fallback_services:
            try:
                return await fallback_service.generate_speech(text, voice_config)
            except Exception as e:
                last_error = e
        
        # If all fail, raise the last error
        raise Exception(f"All TTS services failed. Last error: {last_error}")
```

## Sources
51. ElevenLabs API Documentation - Core Features and Models
52. ElevenLabs Text-to-Speech Integration Patterns
53. ElevenLabs Voice Management for Educational Content
54. ElevenLabs Streaming and Real-time Audio Generation
55. ElevenLabs Cost Optimization and Caching Strategies
56. ElevenLabs Production Integration with FastAPI
57. ElevenLabs Multi-speaker Dialogue Generation
58. ElevenLabs Error Handling and Service Reliability
59. ElevenLabs Audio Processing and Format Optimization
60. ElevenLabs Educational Voice Selection and Audience Adaptation