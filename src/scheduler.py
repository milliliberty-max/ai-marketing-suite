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
            self._setup_auto_agents()

    def _setup_daily_auto_post(self) -> None:
        """Set up auto-post jobs at peak times: 10, 12, 14, 16, 18 UTC (max 5/day)."""
        peak_hours = [10, 12, 14, 16, 18]
        for hour in peak_hours:
            self.scheduler.add_job(
                self._run_daily_auto_post,
                trigger=CronTrigger(hour=hour, minute=0),
                id=f"auto_post_{hour}",
                replace_existing=True,
            )
        logger.info(
            "Auto-post scheduled at peak times: %s UTC (max 5 posts/day, 2h gap)",
            peak_hours,
        )

    def _setup_auto_agents(self) -> None:
        """Set up automatic agent runs."""
        # Daily analysis agents at 9:00 UTC (before posting starts)
        self.scheduler.add_job(
            self._run_daily_agents,
            trigger=CronTrigger(hour=9, minute=0),
            id="daily_agents",
            replace_existing=True,
        )
        # Carousel post at 13:00 UTC (1 per day, between regular posts)
        self.scheduler.add_job(
            self._run_carousel_post,
            trigger=CronTrigger(hour=13, minute=0),
            id="daily_carousel",
            replace_existing=True,
        )
        # Post-analysis after last post at 19:00 UTC
        self.scheduler.add_job(
            self._run_post_analysis,
            trigger=CronTrigger(hour=19, minute=0),
            id="post_analysis",
            replace_existing=True,
        )
        logger.info(
            "Auto agents scheduled: analysis@9UTC, carousel@13UTC, "
            "post-analysis@19UTC"
        )

    async def _run_daily_agents(self) -> None:
        """Run all analysis agents daily."""
        import asyncio

        from src.auto_agents import run_all_analysis_agents

        logger.info("Running daily auto-agents...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_all_analysis_agents)
        logger.info("Daily auto-agents completed.")

    async def _run_carousel_post(self) -> None:
        """Run carousel post if enough images."""
        from src.auto_agents import auto_post_carousel
        from src.auto_poster import get_posts_today_count

        posts_today = get_posts_today_count()
        if posts_today >= 5:
            logger.info("Daily limit reached. Skipping carousel.")
            return

        logger.info("Running auto carousel post...")
        result = await auto_post_carousel()
        logger.info("Carousel result: %s", result.get("status"))

    async def _run_post_analysis(self) -> None:
        """Run performance analysis after daily posts."""
        import asyncio

        from src.auto_agents import run_performance_analysis

        logger.info("Running post-day performance analysis...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_performance_analysis)
        logger.info("Post-analysis completed.")

    async def _run_daily_auto_post(self) -> None:
        """Execute an auto-post if daily limit not reached."""
        from src.auto_poster import auto_post_next_image, get_posts_today_count

        posts_today = get_posts_today_count()
        if posts_today >= 5:
            logger.info("Daily limit reached (%d/5). Skipping.", posts_today)
            return

        logger.info("Running auto-post (%d/5 today)...", posts_today + 1)
        result = await auto_post_next_image()
        logger.info("Auto-post result: %s", result.get("status"))

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
