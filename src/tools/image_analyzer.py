"""Image analysis using Groq Vision API."""

from groq import Groq

from src.config.settings import settings


def analyze_image_from_url(image_url: str, context: str = "") -> str:
    """Analyze an image from a URL and return a detailed description.

    Args:
        image_url: Public URL of the image to analyze.
        context: Optional brand/product context for better analysis.

    Returns:
        Detailed description of the image content.
    """
    client = Groq(api_key=settings.groq_api_key)

    system_prompt = (
        "You are a professional product photographer and fashion copywriter. "
        "Analyze this image in detail. Describe:\n"
        "1. The product(s) shown — materials, colors, textures, embellishments\n"
        "2. The styling and composition of the photo\n"
        "3. The mood and aesthetic it conveys\n"
        "4. Key selling points visible in the image\n"
        "5. Target audience this would appeal to\n"
        "Be specific and detailed — mention exact colors, patterns, "
        "craftsmanship details, and luxury elements you can see."
    )

    if context:
        system_prompt += f"\n\nBrand context: {context}"

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this product image in detail:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            },
        ],
        max_tokens=800,
    )

    return response.choices[0].message.content or ""
