# Setup and Installation

This guide covers how to set up, run, and test **Bot in the Dark**, including using GitHub Codespaces for a quick development environment.

## 1. Create a Discord Bot Account

Before you can run the code, you need a Bot Token from Discord:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name.
3. Navigate to the **Bot** tab on the left menu.
4. Click **Reset Token** (or **Add Bot** if you haven't) to generate your `DISCORD_TOKEN`. **Keep this secret!**
5. Under **Privileged Gateway Intents**, leave **Message Content Intent** off unless you explicitly add classic prefix/message commands.
6. Go to the **OAuth2 -> URL Generator** tab.
7. Check the `bot` and `applications.commands` scopes.
8. Check necessary permissions (e.g., Send Messages, Read Message History).
9. Copy the generated URL at the bottom, paste it into your browser, and invite the bot to your test server.

## 2. Setting up the Environment

The project requires environment variables to run.

1. Copy the example `.env` file to create your own configuration:
   ```bash
   cp .env_example .env
   ```
2. Open the `.env` file and replace the `DISCORD_TOKEN=""` line with the token you generated in step 1:
   ```env
   DISCORD_TOKEN="your-secret-bot-token-here"
   SYNC_COMMANDS=1
   DEV_GUILD_ID=
   ENABLE_MESSAGE_CONTENT_INTENT=0
   ```
   - `SYNC_COMMANDS=1` syncs slash commands at startup.
   - Set `DEV_GUILD_ID` to your test server ID for faster guild-only sync during development.
   - Keep `ENABLE_MESSAGE_CONTENT_INTENT=0` unless you need message content events.

## 3. Running Locally

Make sure you have Python 3.10+ installed.

1. Install the required dependencies from the root directory:
   ```bash
   /workspaces/blades-in-the-bot/.venv/bin/python -m pip install -r requirements.txt
   ```
2. Start the bot:
   ```bash
   /workspaces/blades-in-the-bot/.venv/bin/python main.py
   ```
You should see a message indicating the bot has logged in and synced its slash commands.

### Command Sync Notes

- With `DEV_GUILD_ID` set, commands sync to that guild immediately (best for development).
- Without `DEV_GUILD_ID`, commands sync globally (can take longer to propagate).
- Set `SYNC_COMMANDS=0` to skip syncing on startup.

## 4. Testing with GitHub Codespaces

You can develop and run this bot entirely in your browser using GitHub Codespaces. This is the recommended way to quickly get started without configuring your local machine.

1. On the GitHub repository page, click the green **Code** button.
2. Select the **Codespaces** tab.
3. Click **Create codespace on main** (or the branch you are working on).
4. Once the web-based VS Code environment loads, the terminal will open at the bottom.
5. Follow **Step 2 (Setting up the Environment)** to create your `.env` file and add your `DISCORD_TOKEN` in the Codespaces editor.
6. Install dependencies in the terminal:
   ```bash
   /workspaces/blades-in-the-bot/.venv/bin/python -m pip install -r requirements.txt
   ```
7. Start the bot in the Codespaces terminal:
   ```bash
   /workspaces/blades-in-the-bot/.venv/bin/python main.py
   ```
Your bot is now running from the cloud! You can type `/ping` in your Discord test server to verify it's working.
