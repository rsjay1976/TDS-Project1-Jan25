# Proxy setup for corporate networks (optional)

# Base image
FROM python:latest

# Proxy build args (in case it's needed after FROM)


# Install curl and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -sSfL https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

# Verify uv installation
RUN uv --version

# Set working directory inside the container
WORKDIR /

# Copy application files
COPY execute.py /
COPY data/ /data/

# Default command to run your script with uv
CMD ["uv", "run", "execute.py"]
