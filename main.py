# Libraries
import discord # discord
from discord.ext import commands # slash commands
import nest_asyncio # async functionality
import pandas as pd # simplified backed
import time # time
nest_asyncio.apply() # apply nest_asyncio
from discord.utils import get # idk
import requests # for images and image links in the post system
import uuid # unique ids

# User class to organize members, ids, and nicknames.
class User:
  def __init__(self, member, nick):
    self.member = member # object
    self.ID = str(uuid.uuid4())
    self.nick = nick

  def info(self):
    return (self.member, self.ID, self.nick)
  
# simplified backend for this concept (just for one server)
# please replace with your own database (postgresql or sqlite)
class Server:
  def __init__(self):
    # store the members, unqiue ids, and nicknames
    self.members = []
    self.ids = []
    self.nicks = []

  def take_snapshot(self, client):
    # this is the function to call in on_ready : takes in all the member data on the server and stores it in .
    self.members = []
    self.ids = []
    for index, member in enumerate(client.guilds[0].members):
      U = User(member, index) # User object for organization
      self.members.append(U.info()[0]) # should've made these hashmaps
      self.ids.append(U.info()[1])
      self.nicks.append(U.info()[2])

  def add(self, member_id):
    # adds a member to the storage, useful for when a user joins a server
    print(member_id[0])
    if not member_id[0] in self.members:
      self.members.append(member_id[0])
      self.ids.append(member_id[1])
      self.nicks.append(member_id[2])

  def remove(self, member_id):
    # removes a member to the storage, useful for when a user leaves a server
    self.members.remove(member_id[0])
    self.ids.remove(member_id[1])
    self.nicks.remove(member_id[2])


# Post System Modal Setup (Customize to your will :D )
# mine was based off of 4chan
class Message(discord.ui.Modal, title='Post'):
  # Subject Text Input
  subject = discord.ui.TextInput(
      style=discord.TextStyle.short,
      label='Subject',
      required=True,
      placeholder='Subject'
  )
  # Message Text Input (Bigger)
  message = discord.ui.TextInput(
      style=discord.TextStyle.paragraph,
      label='Content',
      required=True,
      max_length=500,
      placeholder='Enter your thoughts ...'
  )
  # Optional Image (URL)
  img = discord.ui.TextInput(
      style=discord.TextStyle.short,
      label='Image Link',
      required=False,
      max_length=200,
      placeholder='paste image link here ...'
  )

  async def on_submit(self, interaction):
    await interaction.response.defer() # Don't respond to the interaction -> doesn't look clean

    embed = discord.Embed(title=self.subject, description=self.message) # Create Embed Message

    embed.set_thumbnail(url=self.img) # Image is the thumbnail of the Embed

    msg = await interaction.channel.send(embed=embed) # Send the Message
    await msg.publish() # Most IMPORTANT part : posts to the board (public channel in discord) you chose to follow



  async def on_error(self, interaction, error):
    pass # implement your own error handling


server = Server() # initialize backend (Server Object)
channels = [] # keep track of channels

def run():
  client = commands.Bot(command_prefix="/", intents=discord.Intents.all()) # discord boilerplate


  @client.event
  async def on_ready():
    print("ready")
    await client.tree.sync()
    server.take_snapshot(client) # gather and store data
    print(client.guilds) # this concept was tested on only one server, and it should be used that way

    guild = client.guilds[0] # one server I was talking about ^^^^
    admin_role = get(guild.roles, name='Admin') # get the admin role
    # Below is to make the private news (announcement) channels. Each user has their own unqiue private news channel, however admins and the bot has accesss to these
    for member in server.members:
      overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        admin_role: discord.PermissionOverwrite(read_messages=True)
      } # perm config
      memID = server.ids[server.members.index(member)] # get ID
      channel = await guild.create_text_channel(f'{memID}', slowmode_delay=300, overwrites=overwrites, news = True) # creates the private news channel with the ID of the member who uses it
      await channel.send(content='You are limited to 10 Webhooks or Messages, please make thoughful posts', delete_after=15.0) # send a welcome message and warn the user of Discord's webhook limit of 10 per hour

      channels.append(channel.id) # add it to the channel list


  @client.event
  async def on_member_join(member): # handle user joins to backend, overwrite this
    U = User(member, server.nicks[-1] + 1)
    server.add((U.member, U.ID, U.nick))
    await member.edit(nick=server.nicks[server.members.index(member)])

  @client.event
  async def on_member_remove(member): # handle user leaves, overwrite this
    temp_index = server.members.index(member)
    remove_channel = discord.utils.get(client.guilds[0].channels, name=server.ids[temp_index])
    server.remove(server.members[temp_index], server.ids[temp_index], server.nicks[temp_index])
    await client.guilds[0].delete()


  @client.listen('on_message')
  async def remove_normal_msgs(message): # remove normal messages since it doesn't look clean and ruins anonimity
    if not message.embeds:
        await message.delete()


  @client.tree.command() # post command to make a embedded message
  async def post(interaction):
    post_modal = Message()
    await interaction.response.send_modal(post_modal)


  @client.command() # delete private news channels, for testing
  async def delete(ctx):
    guild = client.guilds[0]
    admin_role = get(guild.roles, name='Admin')
    if admin_role in ctx.author.roles:
      for c in channels:
        d = await client.fetch_channel(c)
        await d.delete()


  @client.command(pass_context=True) # members can change nick names
  async def chnick(ctx, member: discord.Member):
    await member.edit(nick=server.nicks[server.members.index(member)])


  client.run() # Your discord bot token


run()