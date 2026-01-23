import discord

class GalleryPaginator(discord.ui.View):
    def __init__(self, ctx, title, tags, image_urls):
        super().__init__()
        self.ctx = ctx
        self.title = title
        self.tags = tags
        self.image_urls = image_urls
        self.num_pages = len(self.image_urls)
        self.current_page = 0

    def create_embed(self):
        embed = discord.Embed(
            title=f"{self.title} - {self.num_pages} Pages",
            description=f"Use the buttons below to scroll\n\n{", ".join(self.tags)}",
            color=0xFF0000
        )
        embed.set_image(url=self.image_urls[self.current_page])
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.num_pages}")
        return embed

    async def update_message(self, interaction: discord.Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.image_urls) - 1:
            self.current_page += 1
            await self.update_message(interaction)