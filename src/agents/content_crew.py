"""CrewAI agents for Instagram content creation and strategy."""

from crewai import Agent, Crew, Process, Task

from src.tools.crewai_tools import get_account_insights, get_recent_posts


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
) -> dict:
    """Run the full content generation crew to create Instagram post content.

    Args:
        topic: The topic or theme for the post.
        brand_voice: The tone and voice to use.
        target_audience: Who the content is for.
        post_type: Type of post (single image, carousel, reel).
        num_posts: Number of post variations to generate.

    Returns:
        Dict with captions, hashtags, and scheduling recommendations.
    """
    strategist = create_content_strategist()
    caption_writer = create_caption_writer()
    hashtag_researcher = create_hashtag_researcher()
    scheduler = create_scheduler_agent()

    strategy_task = Task(
        description=(
            f"Analyze the Instagram account's current performance and recent posts. "
            f"Based on the topic '{topic}', target audience '{target_audience}', "
            f"and post type '{post_type}', provide a brief content strategy including "
            f"key themes, emotional hooks, and engagement tactics to use."
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
            f"Using the content strategy provided, write {num_posts} Instagram "
            f"caption(s) for a {post_type} post about '{topic}'. "
            f"Brand voice: {brand_voice}. Target audience: {target_audience}. "
            f"Each caption should be engaging, include a hook in the first line, "
            f"have a clear CTA, and be optimized for Instagram's algorithm. "
            f"Do NOT include hashtags — those will be added separately."
        ),
        expected_output=(
            f"{num_posts} polished Instagram caption(s), each with: "
            "1) An attention-grabbing first line, "
            "2) Valuable/entertaining body content, "
            "3) A clear call-to-action, "
            "4) Appropriate emoji usage."
        ),
        agent=caption_writer,
        context=[strategy_task],
    )

    hashtag_task = Task(
        description=(
            f"Research and curate 20-30 relevant hashtags for an Instagram post "
            f"about '{topic}' targeting '{target_audience}'. "
            f"Organize them into: "
            f"- 5 high-volume hashtags (500K+ posts), "
            f"- 10 medium-volume hashtags (50K-500K posts), "
            f"- 10 niche hashtags (under 50K posts). "
            f"Also suggest 2-3 branded hashtag ideas."
        ),
        expected_output=(
            "A curated list of 25-30 hashtags organized by volume tier, "
            "plus 2-3 branded hashtag suggestions. "
            "Format each set as a copy-paste ready block."
        ),
        agent=hashtag_researcher,
        context=[strategy_task],
    )

    schedule_task = Task(
        description=(
            "Based on the account's recent posting patterns and engagement data, "
            "recommend the top 3 optimal times to publish this post. "
            "Consider the target audience's likely time zones and activity patterns. "
            "Provide specific days and times (in UTC)."
        ),
        expected_output=(
            "Top 3 recommended posting times with: "
            "1) Specific day and time (UTC), "
            "2) Reasoning for each recommendation, "
            "3) Expected engagement level (high/medium)."
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
    }
