FROM python:3.13.5-slim

LABEL maintainer="mdssa1337@gmail.com"
LABEL authors="medisa"

ENV TZ=Asia/Tomsk
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SE_CACHE_PATH=/tmp/selenium-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    unzip \
    wget \
    curl \
    gnupg \
    ca-certificates \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV CHROMEDRIVER_VERSION="141.0.7390.122"
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN groupadd -r appuser && \
    useradd -r -g appuser -d /home/appuser -s /sbin/nologin -c "App User" appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /tmp/selenium-cache && \
    chown -R appuser:appuser /tmp/selenium-cache

USER appuser

CMD ["python", "indexTelegram.py"]