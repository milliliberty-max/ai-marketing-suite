"""CrewAI agents for advanced Instagram automation features."""

import logging

from crewai import Agent, Crew, Process, Task

logger = logging.getLogger(__name__)

GROQ_MODEL = "groq/llama-3.3-70b-versatile"


# ─── Agent Definitions ───────────────────────────────────────────────


def _performance_tracker() -> Agent:
    return Agent(
        role="Instagram Performance Analyst",
        goal=(
            "Analyze post performance data and identify patterns that drive "
            "engagement for @riverwalk.lhr."
        ),
        backstory=(
            "You are an Instagram analytics expert for luxury brands. You analyze "
            "engagement rates, reach, impressions, saves, and shares to find what "
            "content performs best. You identify winning patterns in captions, "
            "hashtags, posting times, and content types."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _best_time_analyzer() -> Agent:
    return Agent(
        role="Posting Time Optimization Expert",
        goal=(
            "Determine the optimal posting times for @riverwalk.lhr based on "
            "audience behavior and Instagram algorithm patterns."
        ),
        backstory=(
            "You are a social media timing expert. You analyze audience timezone "
            "distribution, engagement patterns by hour and day, and Instagram "
            "algorithm peak windows. You know that posting when your audience is "
            "most active increases reach by 30-50%. You understand the Pakistani "
            "audience (PKT timezone, office hours, late night scrolling)."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _growth_report_agent() -> Agent:
    return Agent(
        role="Follower Growth Report Analyst",
        goal=(
            "Generate comprehensive weekly/monthly growth reports with "
            "actionable insights for @riverwalk.lhr."
        ),
        backstory=(
            "You are a growth marketing analyst for fashion brands. You create "
            "reports that track follower growth rate, engagement rate trends, "
            "top performing posts, content type breakdown, hashtag effectiveness, "
            "and provide specific next-week action items. You present data in "
            "clean, easy-to-read format."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _carousel_creator() -> Agent:
    return Agent(
        role="Carousel Post Strategist",
        goal=(
            "Design engaging carousel post strategies that maximize saves "
            "and shares for @riverwalk.lhr products."
        ),
        backstory=(
            "You are a carousel content expert. You know carousels get 1.4x more "
            "reach and 3.1x more engagement than single images. You design carousel "
            "flows that: 1) Hook on slide 1, 2) Deliver value in middle slides, "
            "3) CTA on last slide. You create educational, storytelling, and "
            "product showcase carousels for luxury accessories."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _before_after_agent() -> Agent:
    return Agent(
        role="Before/After Content Creator",
        goal=(
            "Create compelling before/after and transformation content ideas "
            "for @riverwalk.lhr luxury accessories."
        ),
        backstory=(
            "You are a transformation content specialist. You create before/after "
            "concepts like: packaging → unboxing → styling, plain outfit → with "
            "clutch, raw materials → finished product, behind-the-scenes crafting. "
            "You know transformation content gets 2x more saves and shares."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _ugc_finder_agent() -> Agent:
    return Agent(
        role="User-Generated Content Strategist",
        goal=(
            "Develop UGC strategies and campaigns to encourage customers to "
            "share @riverwalk.lhr products on their profiles."
        ),
        backstory=(
            "You are a UGC marketing expert. You know that UGC has 4.5x higher "
            "conversion rates than branded content. You create hashtag campaigns, "
            "photo contests, customer spotlight features, and incentive programs "
            "that encourage real customers to post about River Walk products."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _trend_meme_agent() -> Agent:
    return Agent(
        role="Trend & Meme Content Creator",
        goal=(
            "Adapt trending Instagram formats and memes for @riverwalk.lhr "
            "luxury accessories to create viral content."
        ),
        backstory=(
            "You are a trend-jacking specialist for fashion brands. You monitor "
            "trending audio, meme formats, viral challenges, and adapt them for "
            "luxury accessories. You know how to make luxury brands feel relatable "
            "without losing their premium image. You follow Pakistani social media "
            "trends and global Instagram trends."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _dm_reply_agent() -> Agent:
    return Agent(
        role="DM Response Template Creator",
        goal=(
            "Create professional, warm DM reply templates for common customer "
            "inquiries to @riverwalk.lhr."
        ),
        backstory=(
            "You are a customer service expert for luxury e-commerce brands. "
            "You create DM templates that: 1) Feel personal, not robotic, "
            "2) Answer the question clearly, 3) Guide toward purchase, "
            "4) Maintain luxury brand voice. You handle pricing inquiries, "
            "availability, custom orders, shipping, and returns in English, "
            "Urdu, and Roman Urdu."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _collab_finder_agent() -> Agent:
    return Agent(
        role="Collaboration & Influencer Strategist",
        goal=(
            "Identify ideal collaboration partners and influencers for "
            "@riverwalk.lhr to grow reach and followers."
        ),
        backstory=(
            "You are an influencer marketing expert for luxury Pakistani brands. "
            "You identify: micro-influencers (1K-10K followers) with high "
            "engagement, complementary brands (bridal wear, jewelry), fashion "
            "bloggers, bridal stylists, and event planners. You create "
            "collaboration proposals and cross-promotion strategies."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _hashtag_tracker_agent() -> Agent:
    return Agent(
        role="Hashtag Performance Analyst",
        goal=(
            "Analyze hashtag effectiveness and recommend optimized hashtag "
            "sets for @riverwalk.lhr posts."
        ),
        backstory=(
            "You are a hashtag strategy expert. You analyze which hashtags drive "
            "the most reach for small accounts. You know the ideal mix: "
            "5 niche (<10K posts), 10 medium (10K-500K), 5 large (500K-2M), "
            "5 broad (2M+), 3 branded. You track which sets perform best "
            "and rotate to avoid shadowbanning."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _facebook_post_agent() -> Agent:
    return Agent(
        role="Facebook Content Adapter",
        goal=(
            "Adapt Instagram content for Facebook to maximize cross-platform "
            "reach for River Walk brand."
        ),
        backstory=(
            "You are a cross-platform social media expert. You know Facebook "
            "and Instagram have different audiences and algorithms. You adapt "
            "captions to be longer and more descriptive for Facebook, use "
            "different hashtag strategies (fewer on FB), and recommend "
            "Facebook-specific features like Groups, Events, and Marketplace."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _pinterest_agent() -> Agent:
    return Agent(
        role="Pinterest Strategy Expert",
        goal=(
            "Create Pinterest-optimized content strategy for River Walk "
            "to drive SEO traffic and brand awareness."
        ),
        backstory=(
            "You are a Pinterest marketing expert for fashion brands. You know "
            "Pinterest is a visual search engine where luxury products thrive. "
            "You create pin descriptions with SEO keywords, design board strategies "
            "(bridal clutches, evening bags, gift ideas), and know that Pinterest "
            "drives 2x more traffic to e-commerce than other social platforms."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _whatsapp_catalog_agent() -> Agent:
    return Agent(
        role="WhatsApp Business Catalog Strategist",
        goal=(
            "Create WhatsApp Business catalog strategies and product descriptions "
            "for River Walk's luxury accessories."
        ),
        backstory=(
            "You are a WhatsApp Business expert for Pakistani e-commerce. You know "
            "that WhatsApp is the #1 communication channel in Pakistan. You create "
            "catalog descriptions, automated greeting messages, quick replies, "
            "and broadcast strategies that drive sales through WhatsApp."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _product_tag_agent() -> Agent:
    return Agent(
        role="Instagram Shopping & Product Tag Specialist",
        goal=(
            "Create product tagging strategies and shoppable post content "
            "for @riverwalk.lhr."
        ),
        backstory=(
            "You are an Instagram Shopping expert. You know how to set up "
            "product catalogs, create shoppable posts, and use product tags "
            "to drive direct sales. You write product descriptions optimized "
            "for Instagram Shop, create collection themes, and know that "
            "shoppable posts get 130% more clicks than non-shoppable ones."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _sale_announcer_agent() -> Agent:
    return Agent(
        role="Sale & Promotion Campaign Creator",
        goal=(
            "Create urgency-driven sale announcements and promotional content "
            "for @riverwalk.lhr that maximize conversions."
        ),
        backstory=(
            "You are a promotional marketing expert for luxury brands. You create "
            "sale campaigns with FOMO, countdown urgency, limited-edition drops, "
            "flash sales, and exclusive discount posts. You balance luxury brand "
            "image with promotional content. You plan around Pakistani events "
            "(Eid sale, wedding season, Independence Day, Valentine's Day)."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


def _order_notification_agent() -> Agent:
    return Agent(
        role="Social Proof & Order Notification Creator",
        goal=(
            "Create 'Just Sold' social proof content and order celebration "
            "posts for @riverwalk.lhr."
        ),
        backstory=(
            "You are a social proof marketing expert. You create 'Just Sold!' "
            "story templates, 'Order packed with love' posts, customer delivery "
            "celebration content, and 'X people viewing this' urgency posts. "
            "You know social proof increases conversions by 270%."
        ),
        llm=GROQ_MODEL,
        verbose=True,
        allow_delegation=False,
    )


# ─── Crew Functions ──────────────────────────────────────────────────


def analyze_performance(post_data: str = "") -> dict:
    """Analyze post performance and identify patterns."""
    agent = _performance_tracker()
    task = Task(
        description=(
            "Analyze the Instagram post performance for @riverwalk.lhr and "
            "provide actionable insights.\n\n"
            f"Post data (if available):\n"
            f"{post_data or 'No specific data — provide general analysis'}\n\n"
            "Provide:\n"
            "1) Which content types perform best (photos vs reels vs carousels)\n"
            "2) Caption length sweet spot\n"
            "3) Hashtag effectiveness analysis\n"
            "4) Engagement rate benchmarks for luxury brands\n"
            "5) Top 5 action items to improve performance"
        ),
        expected_output="Performance analysis with specific metrics and action items.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"performance_report": str(task.output)}


def analyze_best_times(timezone: str = "PKT") -> dict:
    """Analyze best posting times for the target audience."""
    agent = _best_time_analyzer()
    task = Task(
        description=(
            f"Determine the optimal posting times for @riverwalk.lhr.\n"
            f"Primary audience timezone: {timezone} (Pakistan Standard Time)\n"
            f"Secondary audience: UAE, UK, US diaspora\n\n"
            "Provide:\n"
            "1) Best 5 posting times per day (with timezone)\n"
            "2) Best days of the week\n"
            "3) Worst times to avoid\n"
            "4) Weekend vs weekday strategy\n"
            "5) Seasonal adjustments (Ramadan, wedding season, Eid)"
        ),
        expected_output="Optimized posting schedule with specific times and reasoning.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"best_times": str(task.output)}


def generate_growth_report(current_followers: int = 0, total_posts: int = 27) -> dict:
    """Generate a follower growth report."""
    agent = _growth_report_agent()
    task = Task(
        description=(
            f"Generate a growth report for @riverwalk.lhr.\n"
            f"Current followers: {current_followers}\n"
            f"Total posts: {total_posts}\n"
            f"Brand: River Walk — Luxury Handcrafted Accessories, Lahore\n"
            f"Products: Embellished clutches, bridal bags, evening purses\n\n"
            "Include:\n"
            "1) Current status assessment\n"
            "2) Follower growth projection (30/60/90 days)\n"
            "3) Content strategy recommendations\n"
            "4) Engagement improvement tactics\n"
            "5) Weekly action checklist\n"
            "6) Milestone targets (100, 500, 1000 followers)"
        ),
        expected_output="Comprehensive growth report with projections and action items.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"growth_report": str(task.output)}


def create_carousel_strategy(product: str = "luxury clutch") -> dict:
    """Create carousel post strategy."""
    agent = _carousel_creator()
    task = Task(
        description=(
            f"Create a carousel post strategy for @riverwalk.lhr.\n"
            f"Product: {product}\n\n"
            "Design 3 carousel post ideas:\n"
            "For each carousel provide:\n"
            "1) Slide-by-slide content plan (5-10 slides)\n"
            "2) Text overlay for each slide\n"
            "3) Caption for the post\n"
            "4) Hashtags\n"
            "5) CTA on last slide\n\n"
            "Carousel types to cover: Product showcase, Educational/tips, "
            "Storytelling/brand story"
        ),
        expected_output="3 complete carousel post plans with slide-by-slide content.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"carousel_plans": str(task.output)}


def create_before_after(product: str = "luxury clutch") -> dict:
    """Create before/after transformation content ideas."""
    agent = _before_after_agent()
    task = Task(
        description=(
            f"Create 5 before/after transformation content ideas for "
            f"@riverwalk.lhr.\nProduct: {product}\n\n"
            "Ideas should include:\n"
            "1) Packaging → Unboxing → Styling\n"
            "2) Plain outfit → With River Walk accessory\n"
            "3) Raw materials → Crafting → Finished product\n"
            "4) Day look → Evening look with clutch\n"
            "5) Ordinary event → Glamorous event with accessories\n\n"
            "For each idea provide: concept, shot list, caption, hashtags"
        ),
        expected_output="5 before/after content ideas with full production details.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"before_after_ideas": str(task.output)}


def create_ugc_campaign() -> dict:
    """Create user-generated content campaign strategy."""
    agent = _ugc_finder_agent()
    task = Task(
        description=(
            "Create a UGC campaign strategy for @riverwalk.lhr.\n\n"
            "Include:\n"
            "1) Branded hashtag campaign (e.g., #MyRiverWalk)\n"
            "2) Photo contest idea with rules and prizes\n"
            "3) Customer spotlight template (how to feature customers)\n"
            "4) Incentive program (discount for tagging, repost rewards)\n"
            "5) Review/testimonial collection strategy\n"
            "6) Unboxing video encouragement strategy\n"
            "7) Story mention template to repost customer content"
        ),
        expected_output="Complete UGC campaign strategy with templates and examples.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"ugc_campaign": str(task.output)}


def create_trend_content(trend: str = "") -> dict:
    """Create trending/meme content adapted for the brand."""
    agent = _trend_meme_agent()
    task = Task(
        description=(
            "Create 5 trending content ideas for @riverwalk.lhr.\n"
            f"{'Current trend to adapt: ' + trend if trend else 'Use popular trends.'}\n\n"
            "For each idea provide:\n"
            "1) Trend/format name\n"
            "2) How to adapt it for luxury clutches/accessories\n"
            "3) Script/shot plan\n"
            "4) Suggested audio\n"
            "5) Caption and hashtags\n"
            "6) Why this will work for a luxury brand\n\n"
            "Include both global Instagram trends and Pakistani social media trends."
        ),
        expected_output="5 trend-adapted content ideas with full scripts and captions.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"trend_content": str(task.output)}


def generate_dm_templates() -> dict:
    """Generate DM reply templates for common inquiries."""
    agent = _dm_reply_agent()
    task = Task(
        description=(
            "Create DM reply templates for @riverwalk.lhr for these scenarios:\n\n"
            "1) 'Price?' / 'Kitne ka hai?'\n"
            "2) 'Available hai?' / 'Is this still available?'\n"
            "3) 'Custom order ho sakta hai?'\n"
            "4) 'Shipping charges?' / 'Delivery time?'\n"
            "5) 'Do you ship internationally?'\n"
            "6) 'Return/exchange policy?'\n"
            "7) 'Can I get a discount?'\n"
            "8) 'Bulk order for wedding favors?'\n"
            "9) Initial greeting (when someone DMs first)\n"
            "10) Follow-up after inquiry (no response in 24h)\n\n"
            "Each template should be:\n"
            "- Warm and personal, not robotic\n"
            "- In both English and Roman Urdu versions\n"
            "- Guide toward purchase without being pushy\n"
            "- Maintain luxury brand voice"
        ),
        expected_output="10 DM templates in English and Roman Urdu with professional tone.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"dm_templates": str(task.output)}


def find_collaborations() -> dict:
    """Find collaboration and influencer opportunities."""
    agent = _collab_finder_agent()
    task = Task(
        description=(
            "Identify collaboration opportunities for @riverwalk.lhr.\n\n"
            "Provide:\n"
            "1) 5 types of micro-influencers to target (with follower range)\n"
            "2) 5 complementary brand categories for cross-promotion\n"
            "3) Collaboration proposal template (DM/email)\n"
            "4) Content exchange ideas (what to offer, what to ask)\n"
            "5) Giveaway collaboration strategy\n"
            "6) Pakistani fashion blogger outreach plan\n"
            "7) Bridal stylist partnership strategy\n"
            "8) Budget breakdown (free vs paid collaborations)"
        ),
        expected_output="Collaboration strategy with outreach templates and partner categories.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"collaborations": str(task.output)}


def analyze_hashtag_performance() -> dict:
    """Analyze and optimize hashtag strategy."""
    agent = _hashtag_tracker_agent()
    task = Task(
        description=(
            "Create an optimized hashtag strategy for @riverwalk.lhr.\n\n"
            "Provide:\n"
            "1) 5 hashtag sets for different post types:\n"
            "   - Product showcase posts\n"
            "   - Behind-the-scenes posts\n"
            "   - Bridal/wedding posts\n"
            "   - Reels/video posts\n"
            "   - Story posts\n"
            "2) Each set should have 25-30 hashtags with mix:\n"
            "   - 5 niche (<10K posts)\n"
            "   - 10 medium (10K-500K)\n"
            "   - 5 large (500K-2M)\n"
            "   - 5 broad (2M+)\n"
            "   - 3 branded\n"
            "3) Rotation schedule to avoid shadowbanning\n"
            "4) Banned/spam hashtags to avoid"
        ),
        expected_output="5 hashtag sets with rotation schedule and banned hashtag list.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"hashtag_strategy": str(task.output)}


def adapt_for_facebook(instagram_caption: str = "") -> dict:
    """Adapt Instagram content for Facebook."""
    agent = _facebook_post_agent()
    task = Task(
        description=(
            "Create a Facebook content strategy for River Walk brand.\n"
            f"{'Caption: ' + instagram_caption if instagram_caption else 'Original strategy'}\n\n"
            "Provide:\n"
            "1) 5 Facebook-specific post ideas (different from Instagram)\n"
            "2) Facebook Group strategy (create or join)\n"
            "3) Facebook Event strategy for launches/sales\n"
            "4) Facebook Marketplace listing tips\n"
            "5) Cross-posting best practices (what to change from IG to FB)\n"
            "6) Facebook Ad targeting recommendations\n"
            "7) Facebook Shop setup recommendations"
        ),
        expected_output="Facebook content strategy with post ideas and platform-specific tips.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"facebook_strategy": str(task.output)}


def create_pinterest_strategy() -> dict:
    """Create Pinterest content strategy."""
    agent = _pinterest_agent()
    task = Task(
        description=(
            "Create a Pinterest strategy for River Walk luxury accessories.\n\n"
            "Provide:\n"
            "1) 10 Pinterest board ideas with descriptions\n"
            "2) Pin description template with SEO keywords\n"
            "3) Best pin image dimensions and design tips\n"
            "4) Rich Pin setup recommendations\n"
            "5) Pinterest SEO keyword list for luxury accessories\n"
            "6) Pinning schedule (how many pins/day)\n"
            "7) Group board strategy\n"
            "8) Pinterest Ads recommendations"
        ),
        expected_output="Pinterest strategy with board plans, SEO keywords, and pinning schedule.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"pinterest_strategy": str(task.output)}


def create_whatsapp_strategy() -> dict:
    """Create WhatsApp Business catalog strategy."""
    agent = _whatsapp_catalog_agent()
    task = Task(
        description=(
            "Create a WhatsApp Business strategy for River Walk.\n\n"
            "Provide:\n"
            "1) Catalog organization (categories, descriptions)\n"
            "2) Product description templates for catalog\n"
            "3) Automated greeting message\n"
            "4) 10 quick reply templates\n"
            "5) Broadcast list strategy (new arrivals, sales)\n"
            "6) WhatsApp Status content ideas\n"
            "7) Order management workflow via WhatsApp\n"
            "8) Customer follow-up message templates"
        ),
        expected_output="WhatsApp Business strategy with templates and catalog structure.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"whatsapp_strategy": str(task.output)}


def create_product_tags_strategy(products: str = "") -> dict:
    """Create Instagram Shopping product tag strategy."""
    agent = _product_tag_agent()
    task = Task(
        description=(
            "Create an Instagram Shopping strategy for @riverwalk.lhr.\n"
            f"{'Products: ' + products if products else 'Clutches, bridal bags, purses'}\n\n"
            "Provide:\n"
            "1) Product catalog structure (categories, collections)\n"
            "2) Product description template for Instagram Shop\n"
            "3) Shoppable post strategy (when to tag vs not tag)\n"
            "4) Collection themes (Bridal, Evening, Casual, Gift)\n"
            "5) Instagram Shop setup checklist\n"
            "6) Shoppable Reels strategy\n"
            "7) Product launch sequence using Shopping features"
        ),
        expected_output="Instagram Shopping strategy with catalog structure and templates.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"product_tags_strategy": str(task.output)}


def create_sale_campaign(sale_type: str = "seasonal", discount: str = "20%") -> dict:
    """Create a sale/promotion campaign."""
    agent = _sale_announcer_agent()
    task = Task(
        description=(
            f"Create a {sale_type} sale campaign for @riverwalk.lhr.\n"
            f"Discount: {discount}\n\n"
            "Create a complete campaign:\n"
            "1) Pre-sale teaser posts (3 days before)\n"
            "2) Launch announcement post with caption\n"
            "3) Mid-sale reminder post\n"
            "4) Last chance / final hours post\n"
            "5) Story sequence for the sale\n"
            "6) Countdown sticker strategy\n"
            "7) Caption for each post with urgency/FOMO\n"
            "8) Hashtag set for the sale\n"
            "9) DM template for sale inquiries\n"
            "10) Post-sale 'thank you' post"
        ),
        expected_output="Complete sale campaign with all post captions, stories, and timeline.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"sale_campaign": str(task.output)}


def create_order_notification(product_name: str = "luxury clutch") -> dict:
    """Create social proof 'Just Sold' content."""
    agent = _order_notification_agent()
    task = Task(
        description=(
            f"Create social proof content for @riverwalk.lhr.\n"
            f"Product sold: {product_name}\n\n"
            "Create:\n"
            "1) 'Just Sold!' Story template (text + design ideas)\n"
            "2) 'Order packed with love' post caption\n"
            "3) 'X people viewing this right now' urgency template\n"
            "4) Customer delivery celebration post template\n"
            "5) 'Only X left in stock' scarcity template\n"
            "6) Weekly 'Top Sellers' post template\n"
            "7) '100 orders milestone' celebration post\n"
            "8) Review/testimonial spotlight template"
        ),
        expected_output="Social proof content templates with captions for each type.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return {"order_notifications": str(task.output)}
