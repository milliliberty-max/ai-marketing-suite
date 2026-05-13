"""Automatic agent runner — runs all advanced agents on schedule."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
AGENT_RESULTS_FILE = DATA_DIR / "agent_results.json"
UPLOADS_DIR = BASE_DIR / "uploads"


def _load_results() -> dict:
    if AGENT_RESULTS_FILE.exists():
        with open(AGENT_RESULTS_FILE) as f:
            return json.load(f)
    return {}


def _save_results(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(AGENT_RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _store(key: str, value: str) -> None:
    results = _load_results()
    results[key] = {
        "result": value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_results(results)


def get_latest_results() -> dict:
    """Get all latest agent results for dashboard."""
    return _load_results()


# ── Auto Performance Analysis ──────────────────────────────────────────────


def run_performance_analysis() -> str:
    """Analyze post performance automatically."""
    try:
        from src.agents.advanced_crew import analyze_performance

        log_path = DATA_DIR / "auto_post_log.json"
        post_data = ""
        if log_path.exists():
            with open(log_path) as f:
                logs = json.load(f)
            posted = [e for e in logs if e.get("status") == "posted"]
            lines = []
            for p in posted[-10:]:
                lines.append(
                    f"Post: {p.get('filename', '?')} — "
                    f"Caption: {p.get('caption_preview', '')[:80]}"
                )
            post_data = "\n".join(lines)

        result = analyze_performance(post_data)
        report = result.get("performance_report", "")
        _store("performance_tracker", report)
        logger.info("Auto performance analysis completed")
        return report
    except Exception as e:
        logger.error("Auto performance analysis failed: %s", e)
        return f"Error: {e}"


# ── Auto Best Time Analyzer ───────────────────────────────────────────────


def run_best_time_analysis() -> str:
    """Analyze best posting times automatically."""
    try:
        from src.agents.advanced_crew import analyze_best_times

        result = analyze_best_times("PKT")
        report = result.get("best_times", "")
        _store("best_times", report)
        logger.info("Auto best time analysis completed")
        return report
    except Exception as e:
        logger.error("Auto best time analysis failed: %s", e)
        return f"Error: {e}"


# ── Auto Growth Report ─────────────────────────────────────────────────────


def run_growth_report() -> str:
    """Generate daily growth report automatically."""
    try:
        from src.agents.advanced_crew import generate_growth_report

        log_path = DATA_DIR / "auto_post_log.json"
        total_posts = 0
        if log_path.exists():
            with open(log_path) as f:
                logs = json.load(f)
            total_posts = sum(
                1 for e in logs if e.get("status") == "posted"
            )

        result = generate_growth_report(
            current_followers=0, total_posts=total_posts
        )
        report = result.get("growth_report", "")
        _store("growth_report", report)
        logger.info("Auto growth report completed")
        return report
    except Exception as e:
        logger.error("Auto growth report failed: %s", e)
        return f"Error: {e}"


# ── Auto Hashtag Analysis ─────────────────────────────────────────────────


def run_hashtag_analysis() -> str:
    """Analyze hashtag performance automatically."""
    try:
        from src.agents.advanced_crew import analyze_hashtag_performance

        result = analyze_hashtag_performance()
        report = result.get("hashtag_analysis", "")
        _store("hashtag_analysis", report)
        logger.info("Auto hashtag analysis completed")
        return report
    except Exception as e:
        logger.error("Auto hashtag analysis failed: %s", e)
        return f"Error: {e}"


# ── Auto Content Calendar ─────────────────────────────────────────────────


def run_content_calendar() -> str:
    """Generate weekly content calendar automatically."""
    try:
        from src.agents.growth_crew import generate_content_calendar

        result = generate_content_calendar(1)
        report = result.get("content_calendar", "")
        _store("content_calendar", report)
        logger.info("Auto content calendar completed")
        return report
    except Exception as e:
        logger.error("Auto content calendar failed: %s", e)
        return f"Error: {e}"


# ── Auto DM Templates ─────────────────────────────────────────────────────


def run_dm_templates() -> str:
    """Generate DM reply templates automatically."""
    try:
        from src.agents.advanced_crew import generate_dm_templates

        result = generate_dm_templates()
        report = result.get("dm_templates", "")
        _store("dm_templates", report)
        logger.info("Auto DM templates completed")
        return report
    except Exception as e:
        logger.error("Auto DM templates failed: %s", e)
        return f"Error: {e}"


# ── Auto Carousel Post ────────────────────────────────────────────────────


async def auto_post_carousel() -> dict:
    """Create and post a carousel with up to 10 images."""
    from src.agents.content_crew import run_content_generation_crew
    from src.auto_poster import (
        _clean_caption,
        _log_error,
        _log_posted,
        get_posted_images,
    )
    from src.tools.image_uploader import upload_image_to_public_url
    from src.tools.instagram_api import InstagramAPI

    posted = get_posted_images()
    unposted = []
    if UPLOADS_DIR.exists():
        for f in sorted(UPLOADS_DIR.iterdir()):
            ext = f.suffix.lower()
            if ext in {".jpg", ".jpeg", ".png", ".webp"} and f.name not in posted:
                unposted.append(f)

    if len(unposted) < 3:
        logger.info("Not enough images for carousel (%d). Need 3+.", len(unposted))
        return {"status": "skipped", "message": "Need 3+ images for carousel"}

    carousel_images = unposted[:10]
    logger.info(
        "Creating carousel with %d images: %s",
        len(carousel_images),
        [p.name for p in carousel_images],
    )

    public_urls = []
    for img in carousel_images:
        try:
            url = await upload_image_to_public_url(str(img))
            public_urls.append(url)
        except Exception as e:
            logger.error("Carousel image upload failed for %s: %s", img.name, e)

    if len(public_urls) < 3:
        return {"status": "error", "message": "Could not upload enough images"}

    try:
        crew_result = run_content_generation_crew(
            topic="luxury clutch collection showcase carousel",
            brand_voice="luxury and premium",
            target_audience="fashion-conscious women, brides",
            post_type="carousel",
            num_posts=1,
            image_url=public_urls[0],
        )
        caption = crew_result.get("caption", "")
        hashtags = crew_result.get("hashtags", "")
        caption_text = f"{caption}\n\n{hashtags}".strip()
        if not caption_text:
            caption_text = crew_result.get("raw_output", "")
        caption_text = _clean_caption(caption_text)
        if len(caption_text) > 2200:
            caption_text = caption_text[:2197] + "..."
    except Exception as e:
        _log_error("carousel", str(e))
        return {"status": "error", "message": f"Caption generation failed: {e}"}

    try:
        api = InstagramAPI()
        children_ids = []
        for url in public_urls:
            child_id = await api.create_carousel_item(url)
            children_ids.append(child_id)
            logger.info("Carousel item created: %s", child_id)

        import asyncio
        await asyncio.sleep(10)

        container_id = await api.create_carousel_container(
            children_ids, caption_text
        )
        logger.info("Carousel container: %s", container_id)

        await asyncio.sleep(15)

        media_id = await api.publish_media(container_id)
        logger.info("Carousel published: %s", media_id)

        for img in carousel_images:
            _log_posted(img.name, {
                "media_id": media_id,
                "caption_preview": caption_text[:200],
                "post_type": "carousel",
            })

        _store("last_carousel", (
            f"Carousel posted with {len(public_urls)} images. "
            f"Media ID: {media_id}"
        ))

        return {
            "status": "posted",
            "post_type": "carousel",
            "images": len(public_urls),
            "media_id": media_id,
        }
    except Exception as e:
        _log_error("carousel", str(e))
        return {"status": "error", "message": f"Carousel publish failed: {e}"}


# ── Run All Agents ─────────────────────────────────────────────────────────


def run_all_analysis_agents() -> dict:
    """Run all analysis agents (called daily by scheduler)."""
    results = {}
    logger.info("Starting daily auto-agent run...")

    logger.info("[1/5] Running performance analysis...")
    results["performance"] = run_performance_analysis()

    logger.info("[2/5] Running best time analysis...")
    results["best_times"] = run_best_time_analysis()

    logger.info("[3/5] Running growth report...")
    results["growth_report"] = run_growth_report()

    logger.info("[4/5] Running hashtag analysis...")
    results["hashtags"] = run_hashtag_analysis()

    logger.info("[5/5] Running content calendar...")
    results["calendar"] = run_content_calendar()

    logger.info("Daily auto-agent run completed.")
    return results
