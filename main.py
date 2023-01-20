import os
import discord
from discord import ApplicationContext
from together_api import query
discord_token = os.environ.get("DISCORD_TOKEN")
discord_guild = os.environ.get("DISCORD_GUILD")
discord_guild = discord_guild.split(",")

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)
model_name = "together/gpt-neoxT-20B-chat-latest"
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}; model: {model_name}")

@bot.command(guild_ids=discord_guild, description="Chatting with the bot")
async def chat(
        ctx: ApplicationContext,
        context: discord.Option(str, description="The context for the bot to start with", default=None, required=False)
    ):
    thread = await ctx.channel.create_thread(name="LAION / Together Assistant Chat Thread", auto_archive_duration=60, type=discord.ChannelType.public_thread)
    if context:
        with open(f"data/{thread.id}.txt", "w") as f:
            f.write(f"User: {context}\n")
            f.write(f"Assistant: Sure, I will answer your questions based on the given context.\n")
    await ctx.respond("Sure! I'll create a thread for our conversation. Please note that the dialog might be collected anonymously for research purposes.")

@bot.event
async def on_message(msg: discord.Message):
    if isinstance(msg.channel, discord.Thread):
        if msg.channel.owner_id == 1065566651455655946 and not msg.author.bot:
            async with msg.channel.typing():
                content = msg.content
                thread_id = msg.channel.id  # to distinguish between threads
                # save it to database
                with open(f"data/{thread_id}.txt", "a+") as f:
                    f.write(f"User: {content}\n")
                # send it to together api
                with open(f"data/{thread_id}.txt", "r") as f:
                    data = f.read()
                payload = {
                    "model": model_name,
                    "prompt": data,
                    "top_p": 1,
                    "top_k": 40,
                    "temperature": 0.6,
                    "max_tokens": 128,
                }
                response = query(payload)['output']['choices'][0]['text']
                response = response.split("\nUser:")[0]
                with open(f"data/{thread_id}.txt", "a+") as f:
                    f.write(f"{response}\n")
                await msg.reply(response.replace("Assistant:", ""))

bot.run(discord_token)
