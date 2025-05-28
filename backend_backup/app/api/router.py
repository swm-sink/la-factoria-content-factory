from fastapi import APIRouter, BackgroundTasks, Depends, status
from .deps import get_multistep, get_tracker, get_cache
from ..models.schemas import GenerateRequest, GenerateResponse, AudioResponse

router = APIRouter()

@router.post("/generate", 
             status_code=status.HTTP_202_ACCEPTED,
             response_model=GenerateResponse)
async def generate(req: GenerateRequest,
                   ms = Depends(get_multistep)):
    # TODO: Implement job enqueueing
    job_id = "fake-job-id" # Placeholder
    # job_id = await ms.enqueue(req)
    return GenerateResponse(job_id=job_id)

@router.get("/progress/{job_id}")
async def progress(job_id: str, tracker = Depends(get_tracker)):
    # TODO: Implement progress streaming (SSE)
    return {"status": "stub"} # Placeholder # tracker.stream(job_id)

@router.get("/content/{job_id}")
async def content(job_id: str, v: int|None = None, cache = Depends(get_cache)):
    # TODO: Implement content retrieval from cache
    return {"content": "stub"} # Placeholder # await cache.get_content(job_id, version=v)

@router.post("/audio/{job_id}")
async def audio(job_id: str, sample: bool=False, 
                ms=Depends(get_multistep)):
    # TODO: Implement audio synthesis (sample or full)
    url = "fake-audio-url" # Placeholder
    # url = await ms.synthesize(job_id, preview=sample)
    return AudioResponse(url=url) 