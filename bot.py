import discord
import os
import requests
import json
import ssl
import certifi
import asyncio

from io import BytesIO
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
api_url = os.environ["API_URL"]
discord_bot_id = os.environ["DISCORD_BOT_ID"]
discord_bot_token = os.environ["DISCORD_BOT_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]

ssl_context = ssl.create_default_context(cafile=certifi.where())
intents = discord.Intents.default()

intents.messages = True
intents.message_content = True
intents.guild_messages = True

client = discord.Client(intents=intents, ssl_context=ssl_context)
tree = app_commands.CommandTree(client)


async def handleNsfw(message):
    attachment = message.attachments[0]

    url = f"{api_url}/openfaas-opennsfw"
    headers = {"Content-Type": "text/plain"}

    response = requests.post(url, headers=headers, data=attachment.url)
    content = response.content.decode("utf-8")
    result = json.loads(content)

    sfw_score = result["sfw_score"]
    nsfw_score = result["nsfw_score"]

    print("sfw: score: ", sfw_score, "nsfw score: ", nsfw_score)

    msg_to_delete = await message.channel.fetch_message(message.id)

    if nsfw_score > 0.5:
        await msg_to_delete.delete()
        await message.channel.send(
            f'{attachment.url.split("/")[-1]} removed due to displaying explicit or suggestive adult content as it has high NSFW score {nsfw_score}.'
        )
    else:
        await message.channel.send(
            f'{attachment.url.split("/")[-1]} is not removed as it has low NFSW score {nsfw_score}.'
        )


async def handleToxicComment(message):
    url = f"{api_url}/toxic-comment"
    headers = {"Content-Type": "text/plain"}
    response = requests.post(url, headers=headers, data=message.content)
    content = response.content.decode("utf-8")
    result = json.loads(content)
    label = result[0]["label"]
    score = result[0]["score"]
    msg_to_delete = await message.channel.fetch_message(message.id)
    if label == "toxic" and score > 0.7:
        await msg_to_delete.delete()
        await message.channel.send(
            f"message by {message.author} removed due as it is toxic comment"
        )


async def handleChatGpt(message):
    await message.channel.typing()

    async def fetch_messages(message, n):
        return [
            {"author_id": msg.author.id, "content": msg.content}
            async for msg in message.channel.history(limit=n)
        ]

    url = f"{api_url}/chatgpt"
    messages = await fetch_messages(message, 100)
    messages.reverse()
    data = json.dumps(
        {
            "user_id": message.author.id,
            "chatgpt_bot_id": discord_bot_id,
            "messages": messages,
            "channel": message.channel.name,
        }
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    response = requests.post(url, data=data, headers=headers)
    content = response.content.decode("utf-8")
    content = json.loads(content)

    if content.get("response") is not None:
        await message.channel.send(content.get("response"))
    elif content.get("error") is not None:
        await message.channel.send("Error:\n" + content.get("error"))
    else:
        await message.channel.send("Something went wrong. Please try again later.")


@client.event
async def on_message(message):
    # ChatGPT
    if (
        message.type == discord.MessageType.default
        and (message.channel.name == "chatgpt" or message.content.startswith("!chat"))
        and not message.author.bot
    ):
        asyncio.create_task(handleChatGpt(message))
    # Image moderation
    elif message.attachments:
        asyncio.create_task(handleNsfw(message))
    # Toxic Comment Moderation
    elif message.type == discord.MessageType.default and message.author != client.user:
        asyncio.create_task(handleToxicComment(message))


@client.event
async def on_ready():
    synced = await tree.sync()
    print(f"Synced {len(synced)} commands!")


@tree.command(name="image", description="Generate image with DALL·E 2a")
async def image(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)

    data = json.dumps({"prompt": prompt})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    try:
        response = requests.post(api_url + "/dalle2", data=data, headers=headers)
        content = response.content.decode("utf-8")
        content = json.loads(content)

        if content.get("response") is not None:
            image_url = content.get("response")
            image_data = requests.get(image_url).content
            image_file = BytesIO(image_data)
            picture = discord.File(image_file, filename="image.png")

            await interaction.followup.send(file=picture)
        elif content.get("error") is not None:
            await interaction.followup.send("Error:\n" + content.get("error"))
        else:
            await interaction.followup.send(
                "Something went wrong. Please try again later."
            )
    except Exception as e:
        await interaction.followup.send("Error:\n" + str(e))


client.run(discord_bot_token)
