import discord
import os
from GalleryPaginator import GalleryPaginator
from discord.ext import commands
from scraper import scrape_gallery
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="search", help="Searching an NHentai gallery")
async def search(ctx, gallery_id: str):
    await ctx.send(f"🔍 Searching gallery {gallery_id}...")

    result = await scrape_gallery(gallery_id)
    if result is None:
        await ctx.send("❌ Failed to fetch gallery!")
        return

    media_id, num_pages, title, tags, image_urls = result

    embed = discord.Embed(title=f"{title} - {num_pages} Pages", description=f"Use the buttons below to scroll\n\n{", ".join(tags)}", color=0xFF0000)
    embed.set_image(url=image_urls[0])
    embed.set_footer(text=f"Page 1/{num_pages}")

    view = GalleryPaginator(ctx, title, tags, image_urls)
    await ctx.send(embed=embed, view=view)

bot.run(TOKEN)
