# Dev Container base: Python 3.11 + Node 20 via nvm
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Node 20
RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && nvm install 20 && nvm use 20 && corepack enable"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates bash \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
