from discord import Embed

class NamazuEmbed(Embed):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.color = 0xff4448
    # self.set_footer(text='Namazu Bot', icon_url='https://cdn.discordapp.com/avatars/776393355843862548/ec8f4463b6371103a08bd75cabde448c.webp')