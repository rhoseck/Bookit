import logging
import json
from fastapi import Request, Response
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else "unknown",
    }
    
    try:
        start_time = datetime.now(timezone.utc)
        response = await call_next(request)
        duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000  # ms
        log_data["status_code"] = response.status_code
        log_data["duration_ms"] = duration
        logger.info(json.dumps(log_data))
        return response
    except Exception as e:
        log_data["error"] = str(e)
        logger.error(json.dumps(log_data))
        raise