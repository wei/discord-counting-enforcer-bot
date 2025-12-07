# discord-counting-enforcer-bot

A Dockerized Discord bot that enforces strict counting rules in a designated channel.

## Features

- **Positive integers only**: Counting must use positive integers (> 0)
- **Strict increment enforcement**: Each count must be exactly one more than the previous
- **Author lock**: The same person cannot count twice in a row
- **Automatic cleanup**: Invalid messages are deleted immediately

## Environment Variables

The bot requires the following environment variables:

- `DISCORD_TOKEN`: Your Discord bot token
- `DISCORD_SERVER_ID`: The ID of the Discord server to monitor
- `COUNTING_CHANNEL_ID`: The ID of the counting channel to monitor

## Running with Docker

```bash
docker run -e DISCORD_TOKEN=your_token_here \
           -e DISCORD_SERVER_ID=your_server_id \
           -e COUNTING_CHANNEL_ID=your_channel_id \
           ghcr.io/wei/discord-counting-enforcer-bot:latest
```

## Building Locally

```bash
# Build the Docker image
docker build -t discord-counting-bot .

# Run the container
docker run -e DISCORD_TOKEN=your_token_here \
           -e DISCORD_SERVER_ID=your_server_id \
           -e COUNTING_CHANNEL_ID=your_channel_id \
           discord-counting-bot
```

## Rules

1. **Strict Numeric Check**: Message must contain only digits (no spaces, letters, or special characters)
2. **Positive Check**: The number must be greater than zero
3. **Increment Check**: The number must equal the current count + 1
4. **Author Lock**: The message author must be different from the previous author

If any rule fails, the message is deleted immediately.

## Initial State

The first message that is a valid positive integer will initialize the counting state. This message is not deleted.
