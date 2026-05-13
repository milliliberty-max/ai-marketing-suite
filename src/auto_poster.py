"""Automatic daily poster: picks images from folder, generates AI content, posts."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from src.agents.content_crew import run_content_generation_crew
from src.tools.image_uploader import upload_image_to_public_url
from src.tools.instagram_api import InstagramAPI

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
POSTED_LOG = DATA_DIR / "posted_images.json"
AUTO_POST_LOG = DATA_DIR / "auto_post_log.json"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def _load_json(path: Path) -> list:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def _save_json(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_posted_images() -> set[str]:
    """Get set of already-posted image filenames."""
    records = _load_json(POSTED_LOG)
    return {r["filename"] for r in records}


def get_unposted_images() -> list[Path]:
    """Get list of images in uploads folder that haven't been posted."""
    if not UPLOADS_DIR.exists():
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        return []

    posted = get_posted_images()
    unposted = []
    for f in sorted(UPLOADS_DIR.iterdir()):
        if f.suffix.lower() in ALLOWED_EXTENSIONS and f.name not in posted:
            unposted.append(f)
    return unposted


def get_auto_post_log() -> list[dict]:
    """Get the auto-post history log."""
    return _load_json(AUTO_POST_LOG)


def get_posts_today_count() -> int:
    """Count how many posts were successfully made today."""
    today = datetime.now(timezone.utc).date().isoformat()
    log = _load_json(AUTO_POST_LOG)
    return sum(
        1 for entry in log
        if entry.get("status") == "posted"
        and entry.get("timestamp", "").startswith(today)
    )


def _log_posted(filename: str, post_data: dict) -> None:
    """Record that an image was posted."""
    records = _load_json(POSTED_LOG)
    records.append({
        "filename": filename,
        "posted_at": datetime.now(timezone.utc).isoformat(),
        **post_data,
    })
    _save_json(POSTED_LOG, records)

    log = _load_json(AUTO_POST_LOG)
    log.append({
        "filename": filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "posted",
        **post_data,
    })
    _save_json(AUTO_POST_LOG, log)


def _log_error(filename: str, error: str) -> None:
    """Record a failed post attempt."""
    log = _load_json(AUTO_POST_LOG)
    log.append({
        "filename": filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "error": error,
    })
    _save_json(AUTO_POST_LOG, log)


async def auto_post_next_image(
    brand_voice: str = "luxury and premium",
    target_audience: str = "fashion-conscious women, brides",
) -> dict:
    """Pick the next unposted image, generate AI content, and post.

    Returns:
        Dict with post result details.
    """
    unposted = get_unposted_images()
    if not unposted:
        logger.info("No unposted images in uploads folder")
        return {"status": "no_images", "message": "No new images to post"}

    image_path = unposted[0]
    logger.info("Auto-posting image: %s", image_path.name)

    try:
        public_url = await upload_image_to_public_url(str(image_path))
        logger.info("Uploaded to: %s", public_url)
    except Exception as e:
        error_msg = f"Image upload failed: {e}"
        logger.error(error_msg)
        _log_error(image_path.name, error_msg)
        return {"status": "error", "message": error_msg}

    try:
        topic = _guess_topic(image_path.name)
        crew_result = run_content_generation_crew(
            topic=topic,
            brand_voice=brand_voice,
            target_audience=target_audience,
            post_type="single image",
            num_posts=1,
            image_url=public_url,
        )
        caption = crew_result.get("caption", "")
        hashtags = crew_result.get("hashtags", "")
        caption_text = f"{caption}\n\n{hashtags}".strip()
        if not caption_text:
            caption_text = crew_result.get("raw_output", "")
        caption_text = _clean_caption(caption_text)
        if len(caption_text) > 2200:
            caption_text = caption_text[:2197] + "..."
        logger.info("AI caption generated (%d chars)", len(caption_text))
    except Exception as e:
        error_msg = f"AI content generation failed: {e}"
        logger.error(error_msg)
        _log_error(image_path.name, error_msg)
        return {"status": "error", "message": error_msg}

    alt_text = ""
    try:
        image_desc = crew_result.get("image_description", "")
        if image_desc:
            from src.agents.growth_crew import generate_alt_text
            alt_result = generate_alt_text(image_desc)
            alt_text = alt_result.get("alt_text", "")
            logger.info("Alt text generated: %s", alt_text[:80])
    except Exception as e:
        logger.warning("Alt text generation failed (non-critical): %s", e)

    try:
        api = InstagramAPI()
        container_id = await api.create_media_container(
            image_url=public_url,
            caption=caption_text,
        )
        media_id = await api.publish_media(container_id)
        logger.info("Published to Instagram: %s", media_id)

        _log_posted(image_path.name, {
            "media_id": media_id,
            "caption_preview": caption_text[:200],
            "public_url": public_url,
            "alt_text": alt_text,
        })

        return {
            "status": "posted",
            "filename": image_path.name,
            "media_id": media_id,
            "caption_preview": caption_text[:200],
        }
    except Exception as e:
        error_msg = f"Instagram publish failed: {e}"
        logger.error(error_msg)
        _log_error(image_path.name, error_msg)
        return {"status": "error", "message": error_msg}


def _clean_caption(text: str) -> str:
    """Remove markdown formatting from AI-generated captions."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"#{1,3}\s+", "", text)
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if line.startswith("High-Volume Hashtags"):
            continue
        if line.startswith("Medium-Volume Hashtags"):
            continue
        if line.startswith("Niche Hashtags"):
            continue
        if line.startswith("Branded Hashtag"):
            continue
        if "(" in line and "K)" in line:
            tag = line.split("(")[0].strip()
            if tag.startswith("#"):
                cleaned.append(tag)
                continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def _guess_topic(filename: str) -> str:
    """Guess a topic from the filename."""
    name = Path(filename).stem
    name = name.replace("_", " ").replace("-", " ")
    words = [w for w in name.split() if not w.isdigit()]
    if words:
        return " ".join(words)
    return "luxury handcrafted accessories"
