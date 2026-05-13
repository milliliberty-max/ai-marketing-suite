"""Instagram Graph API client for publishing posts."""

import asyncio
import logging

import httpx

from src.config.settings import settings

logger = logging.getLogger(__name__)

IG_GRAPH_API_BASE = "https://graph.instagram.com/v19.0"


class InstagramAPI:
    """Wrapper around Instagram Graph API for publishing content."""

    def __init__(self) -> None:
        self.access_token = settings.instagram_access_token
        self.account_id = settings.instagram_business_account_id
        self.client = httpx.AsyncClient(timeout=60.0)

    async def create_media_container(
        self,
        image_url: str,
        caption: str,
    ) -> str:
        """Create a media container for a single image post.

        Args:
            image_url: Public URL of the image to post.
            caption: Post caption including hashtags.

        Returns:
            The creation_id of the media container.
        """
        url = f"{IG_GRAPH_API_BASE}/{self.account_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        resp = await self.client.post(url, data=payload)
        if resp.status_code != 200:
            logger.error("Instagram API error: %s %s", resp.status_code, resp.text)
        resp.raise_for_status()
        data = resp.json()
        return data["id"]

    async def create_carousel_container(
        self,
        children_ids: list[str],
        caption: str,
    ) -> str:
        """Create a carousel container from multiple media containers.

        Args:
            children_ids: List of media container IDs for carousel items.
            caption: Post caption including hashtags.

        Returns:
            The creation_id of the carousel container.
        """
        url = f"{IG_GRAPH_API_BASE}/{self.account_id}/media"
        payload = {
            "media_type": "CAROUSEL",
            "caption": caption,
            "access_token": self.access_token,
        }
        for i, child_id in enumerate(children_ids):
            payload[f"children[{i}]"] = child_id
        resp = await self.client.post(url, data=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["id"]

    async def create_carousel_item(self, image_url: str) -> str:
        """Create a single carousel item container.

        Args:
            image_url: Public URL of the image.

        Returns:
            The creation_id of the item container.
        """
        url = f"{IG_GRAPH_API_BASE}/{self.account_id}/media"
        payload = {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": self.access_token,
        }
        resp = await self.client.post(url, data=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["id"]

    async def publish_media(self, creation_id: str) -> str:
        """Publish a media container to Instagram.

        Waits for the container to be ready before publishing.

        Args:
            creation_id: The media container ID to publish.

        Returns:
            The published media ID.
        """
        for _ in range(30):
            status = await self.get_media_status(creation_id)
            code = status.get("status_code", "")
            logger.info("Container %s status: %s", creation_id, code)
            if code == "FINISHED":
                break
            if code == "ERROR":
                logger.error("Container error: %s", status)
                raise RuntimeError(f"Media container failed: {status}")
            await asyncio.sleep(2)

        url = f"{IG_GRAPH_API_BASE}/{self.account_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        resp = await self.client.post(url, data=payload)
        if resp.status_code != 200:
            logger.error("Publish error: %s %s", resp.status_code, resp.text)
        resp.raise_for_status()
        data = resp.json()
        return data["id"]

    async def get_media_status(self, media_id: str) -> dict:
        """Check the status of a media container.

        Args:
            media_id: The media container ID.

        Returns:
            Dict with status_code and other info.
        """
        url = f"{IG_GRAPH_API_BASE}/{media_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token,
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_account_insights(self) -> dict:
        """Get basic account insights.

        Returns:
            Dict with follower count, media count, etc.
        """
        url = f"{IG_GRAPH_API_BASE}/me"
        params = {
            "fields": (
                "id,username,account_type,media_count,"
                "followers_count,follows_count,name,biography,profile_picture_url"
            ),
            "access_token": self.access_token,
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_recent_media(self, limit: int = 10) -> list[dict]:
        """Get recent media posts from the account.

        Args:
            limit: Number of posts to retrieve.

        Returns:
            List of media objects with engagement data.
        """
        url = f"{IG_GRAPH_API_BASE}/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count",
            "limit": str(limit),
            "access_token": self.access_token,
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def close(self) -> None:
        await self.client.aclose()


instagram_api = InstagramAPI()
