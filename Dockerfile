FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY main.py .
COPY src/ src/
COPY static/ static/
COPY templates/ templates/

RUN pip install --no-cache-dir -e .

RUN mkdir -p uploads data schedules

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
