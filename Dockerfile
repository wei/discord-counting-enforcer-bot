FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Ensure Python output (prints/logs) is unbuffered so Docker logs show immediately
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Create a non-privileged user and set ownership
RUN useradd -m bot && chown -R bot /app

# Switch to non-root user
USER bot
# Run the bot
CMD ["python", "bot.py"]
