"""FastAPI application for Instagram CrewAI Automation."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.agents.content_crew import run_content_generation_crew
from src.models import (
    ContentGenerationRequest,
    ContentResponse,
    InstantPostRequest,
    PostListResponse,
    SchedulePostRequest,
    ScheduleResponse,
)
from src.scheduler import post_scheduler
from src.tools.instagram_api import instagram_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    post_scheduler.start()
    logger.info("Instagram CrewAI Automation started")
    yield
    post_scheduler.shutdown()
    await instagram_api.close()
    logger.info("Instagram CrewAI Automation stopped")


app = FastAPI(
    title="Instagram CrewAI Automation",
    description="AI-powered Instagram automation with content generation and auto posting",
    version="1.0.0",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ── Dashboard ──────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


# ── Content Generation ─────────────────────────────────────────────────────


@app.post("/api/generate", response_model=ContentResponse)
async def generate_content(req: ContentGenerationRequest):
    """Run CrewAI agents to generate Instagram post content."""
    try:
        result = run_content_generation_crew(
            topic=req.topic,
            brand_voice=req.brand_voice,
            target_audience=req.target_audience,
            post_type=req.post_type,
            num_posts=req.num_posts,
        )
        return ContentResponse(success=True, data=result)
    except Exception as e:
        logger.error("Content generation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Scheduling ─────────────────────────────────────────────────────────────


@app.post("/api/schedule", response_model=ScheduleResponse)
async def schedule_post(req: SchedulePostRequest):
    """Schedule a post for future auto-publishing."""
    if req.scheduled_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

    post_id = post_scheduler.schedule_post(
        image_url=req.image_url,
        caption=req.caption,
        hashtags=req.hashtags,
        scheduled_time=req.scheduled_time,
        image_urls=req.image_urls,
    )
    return ScheduleResponse(
        success=True,
        post_id=post_id,
        scheduled_time=req.scheduled_time.isoformat(),
        message=f"Post scheduled for {req.scheduled_time.isoformat()}",
    )


@app.get("/api/scheduled", response_model=PostListResponse)
async def list_scheduled_posts():
    """List all scheduled posts."""
    posts = post_scheduler.get_all_posts()
    return PostListResponse(success=True, posts=posts, total=len(posts))


@app.delete("/api/schedule/{post_id}")
async def cancel_scheduled_post(post_id: str):
    """Cancel a scheduled post."""
    if post_scheduler.cancel_post(post_id):
        return {"success": True, "message": f"Post {post_id} cancelled"}
    raise HTTPException(status_code=404, detail="Post not found or not cancellable")


# ── Instant Post ───────────────────────────────────────────────────────────


@app.post("/api/post-now")
async def post_now(req: InstantPostRequest):
    """Publish a post to Instagram immediately."""
    try:
        full_caption = f"{req.caption}\n\n{req.hashtags}".strip()
        image_urls = req.image_urls or [req.image_url]

        if len(image_urls) > 1:
            children_ids = []
            for url in image_urls:
                child_id = await instagram_api.create_carousel_item(url)
                children_ids.append(child_id)
            container_id = await instagram_api.create_carousel_container(
                children_ids, full_caption
            )
        else:
            container_id = await instagram_api.create_media_container(
                req.image_url, full_caption
            )

        media_id = await instagram_api.publish_media(container_id)
        return {"success": True, "media_id": media_id, "message": "Post published!"}
    except Exception as e:
        logger.error("Failed to post: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Account Insights ───────────────────────────────────────────────────────


@app.get("/api/insights")
async def get_insights():
    """Get Instagram account insights."""
    try:
        data = await instagram_api.get_account_insights()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error("Failed to get insights: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recent-posts")
async def get_recent_posts(limit: int = 10):
    """Get recent Instagram posts with engagement metrics."""
    try:
        posts = await instagram_api.get_recent_media(limit)
        return {"success": True, "posts": posts, "total": len(posts)}
    except Exception as e:
        logger.error("Failed to get recent posts: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Health ─────────────────────────────────────────────────────────────────


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "instagram-crewai-automation"}
