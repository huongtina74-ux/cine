FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md ./
COPY cinefactory ./cinefactory
COPY config ./config
COPY profiles ./profiles
COPY models ./models
COPY workflows ./workflows
COPY knowledge ./knowledge
RUN pip install --no-cache-dir .
RUN mkdir -p /app/data/projects /app/data/artifacts
EXPOSE 8765
CMD ["uvicorn","cinefactory.api.app:app","--host","0.0.0.0","--port","8765"]
