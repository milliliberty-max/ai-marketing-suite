"""Custom CrewAI tools for Instagram automation."""

from crewai.tools import tool

from src.tools.instagram_api import instagram_api


@tool("Get Instagram Account Insights")
def get_account_insights() -> str:
    """Fetch current Instagram account insights including follower count, media count, and bio.
    Use this to understand the account's current state before creating content."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        data = loop.run_until_complete(instagram_api.get_account_insights())
        return (
            f"Username: {data.get('username', 'N/A')}\n"
            f"Name: {data.get('name', 'N/A')}\n"
            f"Followers: {data.get('followers_count', 'N/A')}\n"
            f"Total Posts: {data.get('media_count', 'N/A')}\n"
            f"Bio: {data.get('biography', 'N/A')}"
        )
    finally:
        loop.close()


@tool("Get Recent Instagram Posts")
def get_recent_posts(limit: int = 10) -> str:
    """Fetch the most recent Instagram posts with engagement metrics.
    Use this to analyze what content is performing well.

    Args:
        limit: Number of recent posts to fetch (default 10).
    """
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        posts = loop.run_until_complete(instagram_api.get_recent_media(limit))
        if not posts:
            return "No recent posts found."
        result_lines = []
        for post in posts:
            caption = (post.get("caption") or "")[:80]
            result_lines.append(
                f"- [{post.get('media_type', 'IMAGE')}] "
                f"Likes: {post.get('like_count', 0)}, "
                f"Comments: {post.get('comments_count', 0)} | "
                f"\"{caption}...\" ({post.get('timestamp', '')})"
            )
        return "\n".join(result_lines)
    finally:
        loop.close()
