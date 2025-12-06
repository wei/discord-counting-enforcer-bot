#!/usr/bin/env python3
"""
Discord Counting Enforcer Bot
Manages a counting channel with strict rule enforcement.
"""

import os
import sys
import discord
from discord.ext import commands


class CountingBot(commands.Bot):
    """Discord bot for enforcing counting rules."""
    
    def __init__(self, server_id: int, channel_id: int):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)
        
        # Configuration from environment variables
        self.server_id = server_id
        self.channel_id = channel_id
        
        # In-memory state
        self.count = None  # Current count (integer or None)
        self.previous_author_id = None  # Previous author ID (string or None)
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"Bot logged in as {self.user}")
        print(f"Monitoring server ID: {self.server_id}")
        print(f"Monitoring channel ID: {self.channel_id}")
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Only process messages from the specified server and channel
        if message.guild is None or message.guild.id != self.server_id:
            return
        
        if message.channel.id != self.channel_id:
            return
        
        # Get message content
        content = message.content.strip()
        
        # Handle empty messages
        if not content:
            if self.count is not None:
                await message.delete()
            return
        
        # Rule 1: Strict numeric check - content must consist strictly of digits
        if not content.isdigit():
            if self.count is not None:  # Only delete if state is initialized
                await message.delete()
            return
        
        # Parse the integer
        parsed_number = int(content)
        
        # Rule 2: Positive check - must be greater than zero
        if parsed_number <= 0:
            if self.count is not None:  # Only delete if state is initialized
                await message.delete()
            return
        
        # Initial state handling
        if self.count is None:
            # First valid message initializes the state (not deleted)
            self.count = parsed_number
            self.previous_author_id = str(message.author.id)
            print(f"State initialized: count={self.count}, author={self.previous_author_id}")
            return
        
        # Rule 3: Increment check - must equal count + 1
        if parsed_number != self.count + 1:
            await message.delete()
            return
        
        # Rule 4: Author lock - author must not be the same as previous
        current_author_id = str(message.author.id)
        if current_author_id == self.previous_author_id:
            await message.delete()
            return
        
        # All rules passed - update state
        self.count = parsed_number
        self.previous_author_id = current_author_id
        print(f"State updated: count={self.count}, author={self.previous_author_id}")


def main():
    """Main entry point."""
    # Validate required environment variables
    required_vars = ["DISCORD_TOKEN", "DISCORD_SERVER_ID", "COUNTING_CHANNEL_ID"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Get Discord token and IDs
    token = os.environ["DISCORD_TOKEN"]
    server_id = int(os.environ["DISCORD_SERVER_ID"])
    channel_id = int(os.environ["COUNTING_CHANNEL_ID"])
    
    # Create and run bot
    bot = CountingBot(server_id, channel_id)
    bot.run(token)


if __name__ == "__main__":
    main()
