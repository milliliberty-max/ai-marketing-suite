"""CrewAI agents for Instagram follower growth optimization."""

import logging

from crewai import Agent, Crew, Process, Task

logger = logging.getLogger(__name__)

GROQ_MODEL = "groq/llama-3.3-70b-versatile"


# ─── Agent Definitions ───────────────────────────────────────────────

def _bio_optimizer() -> Agent:
    return Agent(
        role="Instagram Bio Optimizer",
        goal=(
            "Write the perfect Instagram bio for @riverwalk.lhr that converts "
            "profile visitors into followers. Maximum 150 characters."
        ),
        backstory=(
            "You are an Instagram bio specialist who has optimized bios for "
            "hundreds of luxury fashion brands. You know that a great bio: "
            "1) States what the brand offers in 3-5 words, "
            "2) Shows the unique value proposition, "
            "3) Has a clear CTA (DM/Shop/Link), "
            "4) Uses line breaks and emojis strategically, "
            "5) Includes a branded hashtag. "
            "You write bios that make 70%+ of visitors hit Follow."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _competitor_analyst() -> Agent:
    return Agent(
        role="Competitor & Trend Analyst",
        goal=(
            "Analyze what successful luxury accessory brands do on Instagram "
            "and provide actionable insights for @riverwalk.lhr to copy."
        ),
        backstory=(
            "You are a competitive intelligence expert for fashion Instagram. "
            "You study brands like Judith Leiber, Bottega Veneta, Elan, "
            "Zara, Sana Safinaz and local Pakistani luxury brands. You know "
            "what content formats (reels, carousels, stories), posting "
            "frequency, caption styles, and engagement tactics work best "
            "in the luxury accessories niche."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _comment_reply_agent() -> Agent:
    return Agent(
        role="Community Manager & Comment Responder",
        goal=(
            "Generate warm, engaging, brand-appropriate replies to Instagram "
            "comments that build community and encourage more interaction."
        ),
        backstory=(
            "You are a community manager for luxury fashion brands. You reply "
            "to every comment in a way that: 1) Makes the commenter feel valued, "
            "2) Encourages them to come back, 3) Extends the conversation "
            "(Instagram algorithm rewards comment threads), 4) Naturally promotes "
            "products without being pushy. You match the language of the commenter "
            "(English, Urdu, Roman Urdu)."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _story_content_agent() -> Agent:
    return Agent(
        role="Instagram Story Content Creator",
        goal=(
            "Create engaging Story ideas that drive profile visits, "
            "engagement, and follower growth for @riverwalk.lhr."
        ),
        backstory=(
            "You are a Stories expert who knows that Stories drive 50% of "
            "profile visits. You create: polls, quizzes, 'this or that' "
            "comparisons, behind-the-scenes content, countdown timers for "
            "launches, customer testimonials, and 'swipe up' / 'link in bio' "
            "CTAs. You know that interactive stickers (polls, questions) "
            "boost reach by 40%."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _content_calendar_agent() -> Agent:
    return Agent(
        role="Content Calendar Planner",
        goal=(
            "Create a strategic weekly content calendar for @riverwalk.lhr "
            "that ensures content variety and consistent posting."
        ),
        backstory=(
            "You are a content planning expert for fashion brands. You know "
            "the ideal content mix: 40% product showcases, 20% behind-the-scenes, "
            "15% customer testimonials/UGC, 10% educational/tips, 10% trending "
            "content, 5% brand story. You plan for variety so the feed doesn't "
            "look repetitive. You schedule around key fashion events, seasons, "
            "and Pakistani cultural calendar (Eid, wedding season, etc.)."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _caption_ab_tester() -> Agent:
    return Agent(
        role="Caption A/B Test Specialist",
        goal=(
            "Create two distinct caption variations for each post to identify "
            "which style resonates better with the target audience."
        ),
        backstory=(
            "You are a copywriting strategist who A/B tests everything. "
            "For each post you create: Version A (emotional/storytelling) and "
            "Version B (direct/benefit-focused). You track which approach gets "
            "more engagement over time. You know that testing different hooks, "
            "CTA styles, and caption lengths is key to growth optimization."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _alt_text_agent() -> Agent:
    return Agent(
        role="SEO & Alt Text Optimizer",
        goal=(
            "Write SEO-optimized alt text for Instagram images that helps "
            "the post rank in Instagram's search and Explore algorithm."
        ),
        backstory=(
            "You are an Instagram SEO expert. You know that alt text helps "
            "Instagram's AI understand image content, which improves ranking "
            "in search results and Explore page. You write concise, keyword-rich "
            "alt text (max 100 characters) that describes the product and "
            "includes relevant search terms people use to find luxury accessories."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _reels_script_agent() -> Agent:
    return Agent(
        role="Reels Script Writer",
        goal=(
            "Write short, engaging video scripts for Instagram Reels that "
            "showcase products and drive massive follower growth."
        ),
        backstory=(
            "You are a viral Reels creator for luxury fashion brands. You know "
            "that Reels get 2x more reach than photos. You write scripts that: "
            "1) Hook in first 1 second, 2) Show product transformation or reveal, "
            "3) Use trending audio concepts, 4) End with a follow CTA. "
            "You keep scripts under 30 seconds and suggest trending audio styles. "
            "You write for luxury accessories like clutches, handbags, bridal items."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


# ─── Crew Functions ──────────────────────────────────────────────────

def optimize_bio() -> dict:
    """Run bio optimization crew."""
    agent = _bio_optimizer()
    task = Task(
        description=(
            "Write 3 optimized Instagram bio options for @riverwalk.lhr.\n"
            "Brand: River Walk — Luxury Handcrafted Accessories\n"
            "Products: Embellished clutches, bridal bags, evening purses\n"
            "Location: Lahore, Pakistan\n"
            "Target: Fashion-conscious women, brides, 20-40 age\n\n"
            "Each bio must:\n"
            "- Be under 150 characters\n"
            "- Include what the brand sells\n"
            "- Have a CTA (DM to order / Link in bio)\n"
            "- Include branded hashtag #RiverWalkLuxury\n"
            "- Use emojis strategically\n"
            "- Use line breaks for readability"
        ),
        expected_output=(
            "3 bio options, each under 150 characters, with line breaks, "
            "emojis, value proposition, and CTA."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"bio_options": str(task.output)}


def analyze_competitors() -> dict:
    """Run competitor analysis crew."""
    agent = _competitor_analyst()
    task = Task(
        description=(
            "Analyze the top strategies used by successful luxury accessory "
            "brands on Instagram. Provide actionable recommendations for "
            "@riverwalk.lhr to grow from 0 followers.\n\n"
            "Cover:\n"
            "1) Content formats that work best (reels vs photos vs carousels)\n"
            "2) Posting frequency recommendation\n"
            "3) Caption styles that drive engagement\n"
            "4) Hashtag strategies for small luxury brands\n"
            "5) Story strategies for engagement\n"
            "6) Collaboration/influencer tactics\n"
            "7) Pakistani market specific tips (Eid, wedding season, etc.)"
        ),
        expected_output=(
            "A concise, actionable competitive analysis with specific "
            "recommendations for @riverwalk.lhr to implement immediately."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"analysis": str(task.output)}


def generate_comment_replies(comments: list[str]) -> dict:
    """Generate replies for a list of comments."""
    agent = _comment_reply_agent()
    comments_text = "\n".join(f"- {c}" for c in comments)
    task = Task(
        description=(
            f"Generate warm, engaging replies for these Instagram comments "
            f"on a luxury clutch post by @riverwalk.lhr:\n\n{comments_text}\n\n"
            f"Rules:\n"
            f"- Match the commenter's language (English/Urdu/Roman Urdu)\n"
            f"- Be warm and personal, not robotic\n"
            f"- Extend the conversation with a question when possible\n"
            f"- Subtly promote products without being pushy\n"
            f"- Keep replies under 50 words each"
        ),
        expected_output=(
            "A reply for each comment. Format: 'Comment: ... → Reply: ...'"
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"replies": str(task.output)}


def generate_story_ideas(post_topic: str) -> dict:
    """Generate story ideas related to a post topic."""
    agent = _story_content_agent()
    task = Task(
        description=(
            f"Create 5 Instagram Story ideas to complement a feed post about "
            f"'{post_topic}' by @riverwalk.lhr.\n\n"
            f"Include:\n"
            f"1) A poll story (this or that / yes or no)\n"
            f"2) A quiz story about luxury fashion\n"
            f"3) A behind-the-scenes story idea\n"
            f"4) A countdown/teaser story\n"
            f"5) A 'ask me anything' or Q&A story\n\n"
            f"Each story should include: visual description, text overlay, "
            f"sticker type (poll/quiz/question/countdown), and CTA."
        ),
        expected_output=(
            "5 detailed Story ideas with visual descriptions, "
            "text overlays, interactive stickers, and CTAs."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"story_ideas": str(task.output)}


def generate_content_calendar(weeks: int = 1) -> dict:
    """Generate a content calendar."""
    agent = _content_calendar_agent()
    task = Task(
        description=(
            f"Create a {weeks}-week content calendar for @riverwalk.lhr.\n"
            f"Brand: Luxury handcrafted accessories (clutches, bridal bags)\n"
            f"Posting: 5 posts/day at 10:00, 12:00, 14:00, 16:00, 18:00 UTC\n\n"
            f"For each day, specify:\n"
            f"- Post type (product photo, carousel, reel, behind-scenes, testimonial)\n"
            f"- Content theme/topic\n"
            f"- Caption angle (storytelling, educational, FOMO, engagement)\n"
            f"- Story idea to pair with post\n\n"
            f"Ensure variety: don't repeat same format 2 days in a row.\n"
            f"Include Pakistani cultural events if relevant this month."
        ),
        expected_output=(
            f"A {weeks}-week content calendar in table format with "
            "day, time, post type, topic, and caption angle."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"calendar": str(task.output)}


def generate_ab_captions(topic: str, image_description: str = "") -> dict:
    """Generate A/B test caption variations."""
    agent = _caption_ab_tester()
    image_context = ""
    if image_description:
        image_context = f"\nImage shows: {image_description}\n"
    task = Task(
        description=(
            f"Create 2 caption variations for an Instagram post about "
            f"'{topic}' by @riverwalk.lhr.\n{image_context}\n"
            f"Version A: Emotional/storytelling approach\n"
            f"- Start with a story or emotion\n"
            f"- Build connection with reader\n"
            f"- End with engagement question + follow CTA\n\n"
            f"Version B: Direct/benefit-focused approach\n"
            f"- Start with bold product statement\n"
            f"- List key benefits/features\n"
            f"- End with urgency CTA + follow CTA\n\n"
            f"Both must mention specific product details and include "
            f"'Follow @riverwalk.lhr' CTA."
        ),
        expected_output=(
            "Two distinct caption versions clearly labeled A and B. "
            "Each with different style but both optimized for engagement."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"captions": str(task.output)}


def generate_alt_text(image_description: str) -> dict:
    """Generate SEO-optimized alt text for an image."""
    agent = _alt_text_agent()
    task = Task(
        description=(
            f"Write SEO-optimized alt text for this Instagram image.\n"
            f"Image description: {image_description}\n"
            f"Brand: River Walk (@riverwalk.lhr)\n\n"
            f"Rules:\n"
            f"- Max 100 characters\n"
            f"- Include product type (clutch, handbag, etc.)\n"
            f"- Include key material/color\n"
            f"- Include 'handcrafted' or 'luxury'\n"
            f"- Make it descriptive for Instagram's search algorithm\n"
            f"- Do NOT include hashtags or @mentions"
        ),
        expected_output=(
            "One line of alt text, max 100 characters, "
            "descriptive and keyword-rich."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"alt_text": str(task.output)}


def generate_reel_script(topic: str, product_description: str = "") -> dict:
    """Generate a Reels video script."""
    agent = _reels_script_agent()
    product_ctx = ""
    if product_description:
        product_ctx = f"\nProduct: {product_description}\n"
    task = Task(
        description=(
            f"Write a 15-30 second Instagram Reel script about '{topic}' "
            f"for @riverwalk.lhr.\n{product_ctx}\n"
            f"Format:\n"
            f"[0-1s] HOOK — what appears on screen first (must stop scrolling)\n"
            f"[2-5s] REVEAL — show the product\n"
            f"[5-15s] SHOWCASE — different angles, details, styling\n"
            f"[15-20s] CTA — follow, comment, or visit\n\n"
            f"Include:\n"
            f"- Suggested trending audio style (aesthetic, dramatic reveal, etc.)\n"
            f"- Text overlay for each scene\n"
            f"- Transition suggestions\n"
            f"- Caption for the Reel post\n"
            f"- 10 relevant hashtags"
        ),
        expected_output=(
            "A complete Reel script with timestamp, visuals, text overlay, "
            "audio suggestion, transitions, caption, and hashtags."
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"reel_script": str(task.output)}
