import asyncio
import logging
from datetime import datetime, timezone
from redis import Redis
from rq import Queue

from app.services.feasibility import analyze_idea

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_analysis_sync(idea_id: str, title: str, description: str, constraints: dict, preferences: dict):
    try:
        result = asyncio.run(
            analyze_idea(title, description, constraints, preferences)
        )
        logger.info("Analysis complete for idea %s: verdict=%s", idea_id, result.get("tech_feasibility", {}).get("verdict"))
        return result
    except Exception as e:
        logger.error("Analysis failed for idea %s: %s", idea_id, e)
        return None


def enqueue_analysis(idea_id: str, title: str, description: str, constraints: dict, preferences: dict):
    conn = Redis.from_url("redis://localhost:6379/0")
    q = Queue("feasibility", connection=conn)
    q.enqueue(run_analysis_sync, idea_id, title, description, constraints, preferences)
    logger.info("Enqueued feasibility analysis for idea %s", idea_id)