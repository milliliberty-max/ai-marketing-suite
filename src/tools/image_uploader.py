"""Upload local images to get a public URL for Instagram API."""

import base64
import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

IMGBB_API = "https://api.imgbb.com/1/upload"
FREEIMAGE_API = "https://freeimage.host/api/1/upload"


async def upload_image_to_public_url(image_path: str) -> str:
    """Upload a local image and return a public URL.

    Uses freeimage.host (no API key needed) as primary,
    falls back to serving from the app.

    Args:
        image_path: Local path to the image file.

    Returns:
        Public URL of the uploaded image.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            FREEIMAGE_API,
            data={
                "key": "6d207e02198a847aa98d0a2a901485a5",
                "action": "upload",
                "source": image_data,
                "format": "json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        url = data["image"]["url"]
        logger.info("Image uploaded: %s -> %s", path.name, url)
        return url
