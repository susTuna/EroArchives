import discord
import math
from scraper import scrape_gallery
from gallerypaginator import GalleryPaginator

class ListPaginator(discord.ui.View):
    def __init__(self, ctx, gallery_pairs):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.gallery_pairs = gallery_pairs
        self.current_page = 0
        self.items_per_page = 5
        self.total_pages = math.ceil(len(self.gallery_pairs) / self.items_per_page)
        self.update_ui_elements()

    def create_list_embed(self):
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        
        page_galleries = self.gallery_pairs[start_index:end_index]

        description = ""
        for i, (title, gallery_id) in enumerate(page_galleries, start=start_index + 1):
            description += f"**{i}.** {title}\n"
            
        embed = discord.Embed(
            title="Search Results",
            description=description,
            color=0x2ECC71
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed

    def update_ui_elements(self):
        self.clear_items()

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        current_page_galleries = self.gallery_pairs[start_index:end_index]

        select_options = [
            discord.SelectOption(
                label=f"{i}. {title[:95]}",
                value=str(gallery_id),
                description=f"Select to view gallery ID: {gallery_id}"
            )
            for i, (title, gallery_id) in enumerate(current_page_galleries, start=start_index + 1)
        ]

        if select_options:
            self.add_item(self.GallerySelect(select_options, self.select_callback))
            
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

    async def update_message(self, interaction: discord.Interaction):
        self.update_ui_elements()
        embed = self.create_list_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, row=0)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_message(interaction)

    async def select_callback(self, interaction: discord.Interaction, selected_id: str):
        await interaction.response.edit_message(
            content=f"🔍 Fetching gallery **{selected_id}**...",
            embed=None,
            view=None 
        )
        
        result = await scrape_gallery(selected_id)
        if result is None:
            await interaction.edit_original_response(content="❌ Failed to fetch gallery!")
            return

        media_id, num_pages, title, tags, image_urls = result

        embed = discord.Embed(
            title=f"{title} - {num_pages} Pages",
            description=f"Use the buttons below to scroll\n\n{', '.join(tags)}",
            color=0xFF0000
        )
        embed.set_image(url=image_urls[0])
        embed.set_footer(text=f"Page 1/{num_pages}")

        view = GalleryPaginator(self.ctx, title, tags, image_urls)
        await interaction.edit_original_response(content="", embed=embed, view=view)

    class GallerySelect(discord.ui.Select):
        def __init__(self, options, callback_func):
            super().__init__(
                placeholder="Select a gallery to view...",
                options=options,
                row=1
            )
            self.callback_func = callback_func

        async def callback(self, interaction: discord.Interaction):
            selected_id = self.values[0]
            await self.callback_func(interaction, selected_id)