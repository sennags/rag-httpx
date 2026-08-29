FROM python:3.11-slim

RUN apt-get update && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PORT=7860
EXPOSE 7860
CMD ["python", "-m", "flask", "--app", "web_app", "run", "--host", "0.0.0.0", "--port", "7860"]
