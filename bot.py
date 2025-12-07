#!/usr/bin/env python3
"""
Discord Counting Enforcer Bot
Manages a counting channel with strict rule enforcement.
"""

import os
import re
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv


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
        """Handle incoming messages and enforce counting rules.
        
        Rules enforced (after initialization):
        1. Strict numeric check - ASCII digits only (0-9)
        2. Increment check - must equal count + 1
        3. Author lock - must differ from previous author
        
        Invalid messages are deleted. State updates only on success.
        """
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
                try:
                    await message.delete()
                except (discord.errors.Forbidden, discord.errors.NotFound):
                    print(f"Failed to delete message {message.id}")
            return
        
        # Rule 1: Strict numeric check - content must consist strictly of ASCII digits
        # Using regex ensures only 0-9 digits are accepted (excludes Unicode digits)
        if not re.match(r'^[0-9]+$', content):
            if self.count is not None:  # Only delete if state is initialized
                try:
                    await message.delete()
                except (discord.errors.Forbidden, discord.errors.NotFound):
                    print(f"Failed to delete message {message.id}")
            return
        
        # Parse the integer (guaranteed to be positive due to regex)
        parsed_number = int(content)
        
        # Initial state handling
        if self.count is None:
            # First valid message initializes the state (not deleted)
            self.count = parsed_number
            self.previous_author_id = str(message.author.id)
            print(f"State initialized: count={self.count}, author={self.previous_author_id}")
            return
        
        # Rule 2: Increment check - must equal count + 1
        if parsed_number != self.count + 1:
            try:
                await message.delete()
            except (discord.errors.Forbidden, discord.errors.NotFound):
                print(f"Failed to delete message {message.id}")
            return
        
        # Rule 3: Author lock - author must not be the same as previous
        current_author_id = str(message.author.id)
        if current_author_id == self.previous_author_id:
            try:
                await message.delete()
            except (discord.errors.Forbidden, discord.errors.NotFound):
                print(f"Failed to delete message {message.id}")
            return
        
        # All rules passed - update state
        self.count = parsed_number
        self.previous_author_id = current_author_id
        print(f"State updated: count={self.count}, author={self.previous_author_id}")


def main():
    """Main entry point."""
    load_dotenv() # Load environment variables from .env file

    # Validate required environment variables
    required_vars = ["DISCORD_TOKEN", "DISCORD_SERVER_ID", "COUNTING_CHANNEL_ID"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Get Discord token and IDs
    token = os.environ["DISCORD_TOKEN"]
    
    try:
        server_id = int(os.environ["DISCORD_SERVER_ID"])
        channel_id = int(os.environ["COUNTING_CHANNEL_ID"])
    except ValueError as e:
        print(f"Error: Invalid integer value in environment variables ({e})")
        sys.exit(1)
    
    # Create and run bot
    bot = CountingBot(server_id, channel_id)
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("Error: Invalid Discord token")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Bot failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
