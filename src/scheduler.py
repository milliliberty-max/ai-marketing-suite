"""Auto-scheduling system for Instagram posts using APScheduler."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from src.tools.instagram_api import instagram_api

logger = logging.getLogger(__name__)

SCHEDULE_FILE = Path("schedules/scheduled_posts.json")


class PostScheduler:
    """Manages scheduled Instagram posts."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduled_posts: dict[str, dict] = {}
        self._load_schedule()

    def _load_schedule(self) -> None:
        SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if SCHEDULE_FILE.exists():
            with open(SCHEDULE_FILE) as f:
                self.scheduled_posts = json.load(f)

    def _save_schedule(self) -> None:
        SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(self.scheduled_posts, f, indent=2, default=str)

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Post scheduler started")
            self._restore_pending_jobs()
            self._setup_daily_auto_post()

    def _setup_daily_auto_post(self) -> None:
        """Set up daily auto-post job at 10:00 AM UTC."""
        self.scheduler.add_job(
            self._run_daily_auto_post,
            trigger=CronTrigger(hour=10, minute=0),
            id="daily_auto_post",
            replace_existing=True,
        )
        logger.info("Daily auto-post scheduled for 10:00 UTC")

    async def _run_daily_auto_post(self) -> None:
        """Execute the daily auto-post."""
        from src.auto_poster import auto_post_next_image
        logger.info("Running daily auto-post...")
        result = await auto_post_next_image()
        logger.info("Daily auto-post result: %s", result.get('status'))

    def _restore_pending_jobs(self) -> None:
        now = datetime.now(timezone.utc)
        for post_id, post_data in self.scheduled_posts.items():
            if post_data["status"] != "pending":
                continue
            scheduled_time = datetime.fromisoformat(post_data["scheduled_time"])
            if scheduled_time <= now:
                post_data["status"] = "missed"
                logger.warning("Post %s missed its scheduled time", post_id)
                continue
            self._add_job(post_id, post_data, scheduled_time)
        self._save_schedule()

    def _add_job(self, post_id: str, post_data: dict, scheduled_time: datetime) -> None:
        self.scheduler.add_job(
            self._publish_post,
            trigger=DateTrigger(run_date=scheduled_time),
            args=[post_id],
            id=post_id,
            replace_existing=True,
        )
        logger.info("Scheduled post %s for %s", post_id, scheduled_time)

    async def _publish_post(self, post_id: str) -> None:
        post_data = self.scheduled_posts.get(post_id)
        if not post_data:
            logger.error("Post %s not found in schedule", post_id)
            return

        try:
            post_data["status"] = "publishing"
            self._save_schedule()

            image_url = post_data["image_url"]
            caption = post_data["caption"]
            hashtags = post_data.get("hashtags", "")
            full_caption = f"{caption}\n\n{hashtags}".strip()

            image_urls = post_data.get("image_urls", [])
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
                    image_url, full_caption
                )

            media_id = await instagram_api.publish_media(container_id)

            post_data["status"] = "published"
            post_data["media_id"] = media_id
            post_data["published_at"] = datetime.now(timezone.utc).isoformat()
            self._save_schedule()
            logger.info("Successfully published post %s (media_id: %s)", post_id, media_id)

        except Exception as e:
            post_data["status"] = "failed"
            post_data["error"] = str(e)
            self._save_schedule()
            logger.error("Failed to publish post %s: %s", post_id, e)

    def schedule_post(
        self,
        image_url: str,
        caption: str,
        hashtags: str,
        scheduled_time: datetime,
        image_urls: list[str] | None = None,
    ) -> str:
        """Schedule a new post for future publishing.

        Args:
            image_url: Primary public URL of the image.
            caption: Post caption.
            hashtags: Hashtag string.
            scheduled_time: When to publish (UTC).
            image_urls: Optional list of image URLs for carousel posts.

        Returns:
            The unique post_id.
        """
        post_id = str(uuid.uuid4())[:8]
        post_data = {
            "post_id": post_id,
            "image_url": image_url,
            "image_urls": image_urls or [image_url],
            "caption": caption,
            "hashtags": hashtags,
            "scheduled_time": scheduled_time.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        self.scheduled_posts[post_id] = post_data
        self._save_schedule()
        self._add_job(post_id, post_data, scheduled_time)
        return post_id

    def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post."""
        if post_id not in self.scheduled_posts:
            return False
        post_data = self.scheduled_posts[post_id]
        if post_data["status"] != "pending":
            return False
        try:
            self.scheduler.remove_job(post_id)
        except Exception:
            pass
        post_data["status"] = "cancelled"
        self._save_schedule()
        return True

    def get_all_posts(self) -> list[dict]:
        """Get all scheduled posts sorted by scheduled time."""
        posts = list(self.scheduled_posts.values())
        posts.sort(key=lambda p: p.get("scheduled_time", ""), reverse=True)
        return posts

    def get_post(self, post_id: str) -> dict | None:
        return self.scheduled_posts.get(post_id)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()


post_scheduler = PostScheduler()
