"""CrewAI agents for Instagram content creation and strategy."""

import logging

from crewai import Agent, Crew, Process, Task

from src.tools.crewai_tools import get_account_insights, get_recent_posts
from src.tools.image_analyzer import analyze_image_from_url

logger = logging.getLogger(__name__)


def create_content_strategist() -> Agent:
    return Agent(
        role="Instagram Content Strategist",
        goal=(
            "Analyze the Instagram account's performance and audience to develop "
            "a data-driven content strategy that maximizes engagement and growth."
        ),
        backstory=(
            "You are an expert social media strategist with years of experience "
            "growing Instagram accounts. You analyze engagement metrics, trending "
            "topics, and audience behavior to craft winning strategies."
        ),
        tools=[get_account_insights, get_recent_posts],
        verbose=True,
        allow_delegation=False,
    )


def create_caption_writer() -> Agent:
    return Agent(
        role="Instagram Caption Writer",
        goal=(
            "Write compelling, engaging Instagram captions that drive likes, "
            "comments, and shares. Include relevant hashtags and calls to action."
        ),
        backstory=(
            "You are a creative copywriter specializing in social media content. "
            "You know how to write captions that stop the scroll, tell stories, "
            "and drive engagement. You understand hashtag strategy and Instagram's "
            "algorithm preferences."
        ),
        verbose=True,
        allow_delegation=False,
    )


def create_hashtag_researcher() -> Agent:
    return Agent(
        role="Hashtag Research Specialist",
        goal=(
            "Research and curate the most effective hashtags for each post to "
            "maximize reach and discoverability. Mix popular, niche, and branded "
            "hashtags strategically."
        ),
        backstory=(
            "You are a hashtag research expert who understands Instagram's "
            "discovery algorithm. You know how to find the perfect mix of "
            "high-volume and niche hashtags to maximize post reach without "
            "getting shadowbanned."
        ),
        verbose=True,
        allow_delegation=False,
    )


def create_scheduler_agent() -> Agent:
    return Agent(
        role="Posting Schedule Optimizer",
        goal=(
            "Determine the optimal posting times based on audience activity "
            "patterns and engagement data to maximize visibility and engagement."
        ),
        backstory=(
            "You are a social media analytics expert who specializes in "
            "optimizing posting schedules. You analyze engagement patterns, "
            "time zones, and audience behavior to recommend the best times "
            "to post for maximum impact."
        ),
        tools=[get_recent_posts],
        verbose=True,
        allow_delegation=False,
    )


def run_content_generation_crew(
    topic: str,
    brand_voice: str = "professional yet friendly",
    target_audience: str = "general audience",
    post_type: str = "single image",
    num_posts: int = 1,
    image_url: str = "",
) -> dict:
    """Run the full content generation crew to create Instagram post content.

    Args:
        topic: The topic or theme for the post.
        brand_voice: The tone and voice to use.
        target_audience: Who the content is for.
        post_type: Type of post (single image, carousel, reel).
        num_posts: Number of post variations to generate.
        image_url: Optional image URL to analyze for context.

    Returns:
        Dict with captions, hashtags, and scheduling recommendations.
    """
    image_description = ""
    if image_url:
        try:
            logger.info("Analyzing image: %s", image_url[:80])
            image_description = analyze_image_from_url(
                image_url,
                context=f"Brand: River Walk. Topic: {topic}. "
                f"Audience: {target_audience}",
            )
            logger.info("Image analysis complete")
        except Exception as e:
            logger.error("Image analysis failed: %s", e)
            image_description = ""

    strategist = create_content_strategist()
    caption_writer = create_caption_writer()
    hashtag_researcher = create_hashtag_researcher()
    scheduler = create_scheduler_agent()

    image_context = ""
    if image_description:
        image_context = (
            f"\n\nIMAGE ANALYSIS (what the photo shows):\n"
            f"{image_description}\n\n"
            f"IMPORTANT: Use these specific visual details from the "
            f"image to write authentic, product-specific captions. "
            f"Mention the actual materials, colors, and details "
            f"visible in the photo."
        )

    strategy_task = Task(
        description=(
            f"Analyze the Instagram account's current performance. "
            f"Based on the topic '{topic}', target audience "
            f"'{target_audience}', and post type '{post_type}', "
            f"provide a content strategy with key themes, "
            f"emotional hooks, and engagement tactics."
            f"{image_context}"
        ),
        expected_output=(
            "A concise content strategy with: "
            "1) Key themes to highlight, "
            "2) Emotional hooks to use, "
            "3) Engagement tactics (questions, CTAs), "
            "4) What's working well on the account currently."
        ),
        agent=strategist,
    )

    caption_task = Task(
        description=(
            f"Write {num_posts} professional Instagram caption(s) "
            f"for a {post_type} post about '{topic}'. "
            f"Brand voice: {brand_voice}. "
            f"Target audience: {target_audience}. "
            f"{image_context}"
            f"\nRULES:\n"
            f"- First line must be an attention-grabbing hook\n"
            f"- Describe the ACTUAL product shown in the image\n"
            f"- Mention specific materials, colors, craftsmanship\n"
            f"- Sound premium and luxurious, not generic\n"
            f"- Include a compelling CTA\n"
            f"- Use emojis sparingly and elegantly\n"
            f"- Do NOT include hashtags (added separately)"
        ),
        expected_output=(
            f"{num_posts} polished, professional Instagram caption(s) "
            "that specifically describe the product in the image. "
            "Each must have: an attention-grabbing first line, "
            "product-specific details, and a clear CTA."
        ),
        agent=caption_writer,
        context=[strategy_task],
    )

    hashtag_task = Task(
        description=(
            f"Curate 20-30 relevant hashtags for an Instagram "
            f"post about '{topic}' targeting '{target_audience}'. "
            f"Organize: 5 high-volume (500K+), "
            f"10 medium (50K-500K), 10 niche (under 50K). "
            f"Also suggest 2-3 branded hashtag ideas."
        ),
        expected_output=(
            "A curated list of 25-30 hashtags organized by tier, "
            "plus 2-3 branded hashtag suggestions. "
            "Format as copy-paste ready blocks."
        ),
        agent=hashtag_researcher,
        context=[strategy_task],
    )

    schedule_task = Task(
        description=(
            "Recommend the top 3 optimal times to publish this "
            "post based on engagement patterns. Consider the "
            "target audience's time zones. Provide specific "
            "days and times (in UTC)."
        ),
        expected_output=(
            "Top 3 recommended posting times with: "
            "1) Specific day and time (UTC), "
            "2) Reasoning, 3) Expected engagement level."
        ),
        agent=scheduler,
        context=[strategy_task],
    )

    crew = Crew(
        agents=[strategist, caption_writer, hashtag_researcher, scheduler],
        tasks=[strategy_task, caption_task, hashtag_task, schedule_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "raw_output": str(result),
        "topic": topic,
        "brand_voice": brand_voice,
        "target_audience": target_audience,
        "post_type": post_type,
        "image_analyzed": bool(image_description),
        "image_description": image_description[:300] if image_description else "",
    }
