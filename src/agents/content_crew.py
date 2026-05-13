"""CrewAI agents for Instagram content creation and strategy."""

import logging

from crewai import Agent, Crew, Process, Task

from src.tools.image_analyzer import analyze_image_from_url

logger = logging.getLogger(__name__)

GROQ_MODEL = "groq/llama-3.3-70b-versatile"


def create_content_strategist() -> Agent:
    return Agent(
        role="Instagram Content Strategist",
        goal=(
            "Analyze the Instagram account's performance and audience to develop "
            "a data-driven content strategy that maximizes engagement, follower "
            "growth, and reach. Every post must be optimized to attract NEW followers."
        ),
        backstory=(
            "You are an expert social media strategist who has grown accounts from "
            "0 to 100K+ followers. You know exactly what makes people hit Follow: "
            "shareable content, relatable hooks, trending formats, and strategic "
            "engagement tactics. You focus on REACH and DISCOVERY over vanity metrics."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def create_caption_writer() -> Agent:
    return Agent(
        role="Instagram Caption Writer",
        goal=(
            "Write compelling, scroll-stopping Instagram captions that drive "
            "likes, comments, shares, saves, AND new followers. Every caption "
            "must include a reason for new visitors to FOLLOW the account."
        ),
        backstory=(
            "You are a viral copywriter specializing in luxury fashion Instagram. "
            "You write captions that: 1) Stop the scroll with a powerful first line, "
            "2) Tell a story about the product, 3) Create FOMO, 4) Ask engaging "
            "questions that drive comments (boosting algorithm reach), 5) Include "
            "a clear CTA to follow for more. You know that SAVES and SHARES are "
            "the strongest signals for Instagram's algorithm to show posts to "
            "new audiences on Explore page."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def create_hashtag_researcher() -> Agent:
    return Agent(
        role="Hashtag Research Specialist",
        goal=(
            "Research and curate the most effective hashtags to get the post "
            "on Instagram's Explore page and reach NEW audiences. Focus on "
            "hashtags where the account can realistically rank in Top Posts."
        ),
        backstory=(
            "You are a hashtag growth expert who has helped small accounts get "
            "discovered. You know that for accounts with 0-1K followers, ranking "
            "in small-to-medium hashtags (under 100K posts) is more effective "
            "than competing in million-post hashtags. You strategically mix: "
            "3 large hashtags for exposure, 10 medium for competition, "
            "15 small/niche for ranking in Top Posts, and 2-3 branded hashtags."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def create_follower_growth_agent() -> Agent:
    return Agent(
        role="Follower Growth Strategist",
        goal=(
            "Optimize every aspect of the post for maximum follower growth. "
            "Analyze what makes people follow luxury fashion accounts and "
            "ensure each post is crafted to convert viewers into followers."
        ),
        backstory=(
            "You are an Instagram growth hacker specializing in luxury fashion "
            "brands. You know the psychology of why people follow accounts: "
            "consistent aesthetic, value proposition, FOMO, exclusivity, and "
            "community. You optimize posts for the Explore page algorithm by "
            "maximizing saves, shares, and comment conversations. You know "
            "that accounts grow fastest when they: post consistently, use "
            "carousel posts, create saveable content (tips, guides), encourage "
            "shares, and build a recognizable brand aesthetic. For a brand "
            "starting at 0 followers, your priority is REACH over engagement rate."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def create_engagement_optimizer() -> Agent:
    return Agent(
        role="Engagement & Virality Optimizer",
        goal=(
            "Add viral elements and engagement triggers to every post that "
            "encourage saves, shares, comments, and follows from new audiences."
        ),
        backstory=(
            "You are a virality expert who studies what makes Instagram posts "
            "blow up. You add elements like: debate-starting questions, "
            "'save this for later' prompts, 'tag someone who needs this', "
            "'share to your story' CTAs, relatable statements that make "
            "people tag friends, and mini-guides or tips that people save. "
            "You know that Instagram's algorithm rewards posts with high "
            "save-to-impression and share-to-impression ratios."
        ),
        llm=GROQ_MODEL,
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
    growth_agent = create_follower_growth_agent()
    engagement_optimizer = create_engagement_optimizer()

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

    account_context = (
        "\n\nACCOUNT STATUS: Brand new account with 0 followers. "
        "Brand: River Walk (@riverwalk.lhr) — luxury handcrafted accessories "
        "(clutches, handbags, bridal accessories). Based in Lahore, Pakistan. "
        "PRIMARY GOAL: Grow from 0 to 1000 followers as fast as possible. "
        "Every post must be optimized for DISCOVERY and FOLLOW conversion."
    )

    strategy_task = Task(
        description=(
            f"Create a follower-growth-focused content strategy for this post. "
            f"Topic: '{topic}', target audience: '{target_audience}', "
            f"post type: '{post_type}'. "
            f"{account_context}"
            f"{image_context}\n\n"
            f"Focus on: 1) How to make this post reach the Explore page, "
            f"2) What hooks will make new viewers follow, "
            f"3) What engagement triggers to use (questions, polls, debates), "
            f"4) How to create FOMO and exclusivity."
        ),
        expected_output=(
            "A growth-focused strategy with: "
            "1) Viral hook ideas for first line, "
            "2) Engagement triggers (questions that drive comments), "
            "3) Save/share-worthy elements to add, "
            "4) Follow CTA approach."
        ),
        agent=strategist,
    )

    caption_task = Task(
        description=(
            f"Write {num_posts} VIRAL Instagram caption(s) "
            f"for a {post_type} post about '{topic}'. "
            f"Brand voice: {brand_voice}. "
            f"Target audience: {target_audience}. "
            f"{image_context}"
            f"\nRULES FOR FOLLOWER GROWTH:\n"
            f"- First line: POWERFUL scroll-stopping hook (question, bold statement, or mystery)\n"
            f"- Describe the ACTUAL product shown in the image with specific details\n"
            f"- Mention specific materials, colors, craftsmanship visible in photo\n"
            f"- Create FOMO: 'limited edition', 'selling fast', 'DM to order'\n"
            f"- Ask an engaging QUESTION that drives comments (algorithm loves comments)\n"
            f"- Add 'Save this for your bridal inspo' or similar save-trigger\n"
            f"- End with FOLLOW CTA: 'Follow @riverwalk.lhr for daily luxury drops'\n"
            f"- Use emojis sparingly and elegantly\n"
            f"- Do NOT include hashtags (added separately)\n"
            f"- Keep caption under 300 words — concise but powerful"
        ),
        expected_output=(
            f"{num_posts} viral, follower-growth-optimized Instagram caption(s). "
            "Must have: scroll-stopping first line, product-specific details, "
            "engagement question, save trigger, and follow CTA."
        ),
        agent=caption_writer,
        context=[strategy_task],
    )

    hashtag_task = Task(
        description=(
            f"Curate 25-30 hashtags optimized for a NEW account (0 followers) "
            f"posting about '{topic}' targeting '{target_audience}'. "
            f"{account_context}\n\n"
            f"STRATEGY FOR SMALL ACCOUNTS:\n"
            f"- 3 large hashtags (500K-2M posts) — for exposure\n"
            f"- 10 medium hashtags (50K-500K) — realistic competition\n"
            f"- 12 small/niche hashtags (under 50K) — can rank in Top Posts\n"
            f"- 3 branded hashtags for River Walk\n"
            f"Output ONLY the hashtags, one per line, starting with #. No categories."
        ),
        expected_output=(
            "25-30 hashtags, one per line, each starting with #. "
            "No category headers, no explanations, just hashtags."
        ),
        agent=hashtag_researcher,
        context=[strategy_task],
    )

    growth_task = Task(
        description=(
            "Review the caption and hashtags generated by the team. "
            "Provide specific suggestions to make this post MORE effective "
            "at gaining followers. Consider:\n"
            "1) Is the first line strong enough to stop scrolling?\n"
            "2) Does it have a clear reason to follow @riverwalk.lhr?\n"
            "3) Will people SAVE or SHARE this post?\n"
            "4) Is there a comment-driving question?\n"
            "5) Are hashtags optimized for a 0-follower account?\n"
            "Give a final optimized version of the caption incorporating "
            "your growth improvements."
        ),
        expected_output=(
            "An optimized final caption that incorporates all growth "
            "improvements. This should be the BEST possible version "
            "for gaining followers. Include the follow CTA."
        ),
        agent=growth_agent,
        context=[caption_task, hashtag_task],
    )

    engagement_task = Task(
        description=(
            "Add final viral engagement triggers to the optimized caption. "
            "Add ONE of these elements if not already present:\n"
            "- 'Double tap if you love this' or similar\n"
            "- 'Tag your bestie who needs this'\n"
            "- 'Save this for your [occasion] inspo'\n"
            "- 'Share to your story if you agree'\n"
            "Keep it natural, not spammy. Output ONLY the final "
            "ready-to-post caption text. No explanations."
        ),
        expected_output=(
            "The final, ready-to-post caption with all engagement "
            "triggers naturally integrated. Just the caption text, "
            "nothing else."
        ),
        agent=engagement_optimizer,
        context=[growth_task],
    )

    crew = Crew(
        agents=[
            strategist, caption_writer, hashtag_researcher,
            growth_agent, engagement_optimizer,
        ],
        tasks=[
            strategy_task, caption_task, hashtag_task,
            growth_task, engagement_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    final_caption = str(engagement_task.output) if engagement_task.output else ""
    if not final_caption:
        final_caption = str(growth_task.output) if growth_task.output else ""
    if not final_caption:
        final_caption = str(caption_task.output) if caption_task.output else ""
    hashtag_output = str(hashtag_task.output) if hashtag_task.output else ""

    return {
        "raw_output": f"{final_caption}\n\n{hashtag_output}",
        "caption": final_caption,
        "hashtags": hashtag_output,
        "topic": topic,
        "brand_voice": brand_voice,
        "target_audience": target_audience,
        "post_type": post_type,
        "image_analyzed": bool(image_description),
        "image_description": image_description[:300] if image_description else "",
    }
