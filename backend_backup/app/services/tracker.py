class ProgressTracker:
    def __init__(self, redis):
        self.redis = redis

    async def start(self, job_id: str):
        # TODO: Start tracking a job
        pass

    async def update(self, job_id: str, stage: str, pct: float, msg: str):
        # TODO: Update progress and publish via pub/sub
        pass

    async def stream(self, job_id: str):
        # TODO: Stream progress updates (SSE)
        yield {"stage": "stub", "pct": 0, "msg": "not implemented"}

    async def cleanup(self):
        # TODO: Cleanup old jobs by TTL
        pass

    # TODO: Add methods for tracking progress (start, update, stream, cleanup)
    pass 