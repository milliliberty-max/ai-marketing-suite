"""FastAPI application for Instagram CrewAI Automation."""

import logging
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.agents.content_crew import run_content_generation_crew
from src.agents.growth_crew import (
    analyze_competitors,
    generate_ab_captions,
    generate_alt_text,
    generate_comment_replies,
    generate_content_calendar,
    generate_reel_script,
    generate_story_ideas,
    optimize_bio,
)
from src.auto_poster import (
    auto_post_next_image,
    get_auto_post_log,
    get_posts_today_count,
    get_unposted_images,
)
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
    (BASE_DIR / "uploads").mkdir(exist_ok=True)
    (BASE_DIR / "data").mkdir(exist_ok=True)
    (BASE_DIR / "schedules").mkdir(exist_ok=True)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ── Dashboard ──────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    insights = {}
    recent = []
    scheduled_posts = post_scheduler.get_all_posts()
    pending_count = len([p for p in scheduled_posts if p["status"] == "pending"])

    try:
        insights = await instagram_api.get_account_insights()
    except Exception as e:
        logger.error("Dashboard insights error: %s", e)

    try:
        recent = await instagram_api.get_recent_media(6)
    except Exception as e:
        logger.error("Dashboard recent posts error: %s", e)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "insights": insights,
            "recent_posts": recent,
            "pending_count": pending_count,
        },
    )


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
            image_url=req.image_url,
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


# ── Auto Poster (Folder-based) ─────────────────────────────────────────────


UPLOADS_DIR = BASE_DIR / "uploads"


@app.post("/api/upload-images")
async def upload_images(files: list[UploadFile]):
    """Upload images to the auto-post folder."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    uploaded = []
    for file in files:
        if not file.filename:
            continue
        dest = UPLOADS_DIR / file.filename
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        uploaded.append(file.filename)
    return {
        "success": True,
        "uploaded": uploaded,
        "total": len(uploaded),
    }


@app.post("/upload")
async def upload_images_form(files: list[UploadFile]):
    """Upload images via traditional form POST (for tunnel access)."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for file in files:
        if not file.filename:
            continue
        dest = UPLOADS_DIR / file.filename
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
    return RedirectResponse(url="/auto-poster", status_code=303)


@app.post("/trigger-auto-post")
async def trigger_auto_post_form():
    """Trigger auto-post via form POST (for tunnel access)."""
    await auto_post_next_image()
    return RedirectResponse(url="/auto-poster", status_code=303)


@app.get("/api/folder-status")
async def folder_status():
    """Get status of the uploads folder."""
    unposted = get_unposted_images()
    post_log = get_auto_post_log()
    return {
        "success": True,
        "unposted_count": len(unposted),
        "unposted_files": [f.name for f in unposted],
        "total_posted": len([p for p in post_log if p["status"] == "posted"]),
        "recent_log": post_log[-10:],
    }


@app.get("/auto-poster", response_class=HTMLResponse)
async def auto_poster_page(request: Request):
    """Server-rendered Auto Poster page."""
    unposted = get_unposted_images()
    post_log = get_auto_post_log()
    return templates.TemplateResponse(
        request=request,
        name="auto_poster.html",
        context={
            "unposted_count": len(unposted),
            "unposted_files": [f.name for f in unposted],
            "total_posted": len(
                [p for p in post_log if p["status"] == "posted"]
            ),
            "posts_today": get_posts_today_count(),
            "recent_log": post_log[-10:],
        },
    )


@app.post("/api/auto-post-now")
async def trigger_auto_post():
    """Manually trigger an auto-post right now."""
    result = await auto_post_next_image()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return {"success": True, **result}


# ── Growth Tools ───────────────────────────────────────────────────────────

@app.post("/api/growth/optimize-bio")
async def api_optimize_bio():
    """Generate optimized Instagram bio options."""
    result = optimize_bio()
    return {"success": True, **result}


@app.post("/api/growth/competitor-analysis")
async def api_competitor_analysis():
    """Run competitor analysis for growth insights."""
    result = analyze_competitors()
    return {"success": True, **result}


@app.post("/api/growth/comment-replies")
async def api_comment_replies(request: Request):
    """Generate reply suggestions for comments."""
    data = await request.json()
    comments = data.get("comments", [])
    if not comments:
        raise HTTPException(status_code=400, detail="No comments provided")
    result = generate_comment_replies(comments)
    return {"success": True, **result}


@app.post("/api/growth/story-ideas")
async def api_story_ideas(request: Request):
    """Generate story ideas for a topic."""
    data = await request.json()
    topic = data.get("topic", "luxury handcrafted accessories")
    result = generate_story_ideas(topic)
    return {"success": True, **result}


@app.post("/api/growth/content-calendar")
async def api_content_calendar(request: Request):
    """Generate a content calendar."""
    data = await request.json()
    weeks = data.get("weeks", 1)
    result = generate_content_calendar(weeks)
    return {"success": True, **result}


@app.post("/api/growth/ab-captions")
async def api_ab_captions(request: Request):
    """Generate A/B test caption variations."""
    data = await request.json()
    topic = data.get("topic", "luxury clutch")
    image_description = data.get("image_description", "")
    result = generate_ab_captions(topic, image_description)
    return {"success": True, **result}


@app.post("/api/growth/alt-text")
async def api_alt_text(request: Request):
    """Generate SEO-optimized alt text."""
    data = await request.json()
    image_description = data.get("image_description", "")
    if not image_description:
        raise HTTPException(status_code=400, detail="No image description provided")
    result = generate_alt_text(image_description)
    return {"success": True, **result}


@app.post("/api/growth/reel-script")
async def api_reel_script(request: Request):
    """Generate a Reel video script."""
    data = await request.json()
    topic = data.get("topic", "luxury clutch showcase")
    product_description = data.get("product_description", "")
    result = generate_reel_script(topic, product_description)
    return {"success": True, **result}


@app.get("/growth-tools", response_class=HTMLResponse)
async def growth_tools_page(request: Request):
    """Growth tools dashboard page."""
    return templates.TemplateResponse(
        request=request,
        name="growth_tools.html",
        context={},
    )


# ── Health ─────────────────────────────────────────────────────────────────


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "instagram-crewai-automation"}
