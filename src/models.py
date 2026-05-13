"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class ContentGenerationRequest(BaseModel):
    topic: str = Field(..., description="Topic or theme for the Instagram post")
    brand_voice: str = Field(
        default="professional yet friendly",
        description="Tone and voice style",
    )
    target_audience: str = Field(
        default="general audience",
        description="Target audience description",
    )
    post_type: str = Field(
        default="single image",
        description="Post type: single image, carousel, or reel",
    )
    num_posts: int = Field(default=1, ge=1, le=5, description="Number of variations")


class SchedulePostRequest(BaseModel):
    image_url: str = Field(..., description="Public URL of the image to post")
    caption: str = Field(..., description="Post caption")
    hashtags: str = Field(default="", description="Hashtags to include")
    scheduled_time: datetime = Field(..., description="When to publish (UTC ISO format)")
    image_urls: list[str] | None = Field(
        default=None,
        description="List of image URLs for carousel posts",
    )


class InstantPostRequest(BaseModel):
    image_url: str = Field(..., description="Public URL of the image to post")
    caption: str = Field(..., description="Post caption")
    hashtags: str = Field(default="", description="Hashtags to include")
    image_urls: list[str] | None = Field(
        default=None,
        description="List of image URLs for carousel posts",
    )


class ContentResponse(BaseModel):
    success: bool
    data: dict


class ScheduleResponse(BaseModel):
    success: bool
    post_id: str
    scheduled_time: str
    message: str


class PostListResponse(BaseModel):
    success: bool
    posts: list[dict]
    total: int
