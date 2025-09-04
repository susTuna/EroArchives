import discord
import os
from gallerypaginator import GalleryPaginator
from listpaginator import ListPaginator
from discord.ext import commands
from scraper import scrape_gallery, scrape_title
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="search", help="Searching an NHentai gallery")
async def search(ctx, *, query: str):
    if query.isdigit():
        await ctx.send(f"🔍 Searching gallery {query}...")
        result = await scrape_gallery(query)

        if result is None:
            await ctx.send("❌ Failed to fetch gallery!")
            return

        num_pages, title, tags, image_urls = result

        embed = discord.Embed(title=f"{title} - {num_pages} Pages", description=f"Use the buttons below to scroll\n\n{", ".join(tags)}", color=0xFF0000)
        embed.set_image(url=image_urls[0])
        embed.set_footer(text=f"Page 1/{num_pages}")

        view = GalleryPaginator(ctx, title, tags, image_urls)
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send(f"🔍 Searching for {query}...")
        gallery_pairs = await scrape_title(query)
        
        if not gallery_pairs:
            await ctx.send(f"❌ No results found for '{query}'.")
            return
            
        view = ListPaginator(ctx, gallery_pairs)
        embed = view.create_list_embed()
        await ctx.send(embed=embed, view=view)
    
bot.run(TOKEN)
