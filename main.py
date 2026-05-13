"""Entry point for the Instagram CrewAI Automation app."""

from src.app import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
