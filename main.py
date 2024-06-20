import discord
from discord.ext import commands
import nest_asyncio
nest_asyncio.apply()
import pandas as pd
import time
import asyncio
import uuid

class Server:
  def __init__(self):
    self.members = []
    self.ids = []
    self.nicks = []

  def take_snapshot(self, client):
    self.members = []
    self.ids = []
    for index, member in enumerate(client.guilds[1].members):
      U = User(member, index)
      self.members.append(U.info()[0])
      self.ids.append(U.info()[1])
      self.nicks.append(U.info()[2])

  def add(self, member_id):
    print(member_id[0])
    if not member_id[0] in self.members:
      self.members.append(member_id[0])
      self.ids.append(member_id[1])
      self.nicks.append(member_id[2])

  def remove(self, member_id):
    self.members.remove(member_id[0])
    self.ids.remove(member_id[1])
    self.nicks.remove(member_id[2])

class User:
  def __init__(self, member, nick):
    self.member = member # object
    self.ID = str(uuid.uuid4())
    self.nick = nick

  def info(self):
    return (self.member, self.ID, self.nick)

server = Server()
channels = []

def run():
  client = commands.Bot(command_prefix="/", intents=discord.Intents.all())


  @client.event
  async def on_ready():
    print("ready")
    server.take_snapshot(client)

    guild = client.guilds[1]
    admin_role = get(guild.roles, name='Admin')
    for member in server.members:
      overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        admin_role: discord.PermissionOverwrite(read_messages=True)
      }
      memID = server.ids[server.members.index(member)]
      channel = await guild.create_text_channel(f'{memID}', news=True, slowmode_delay=1800, overwrites=overwrites)
      await channel.send(content='You are limited to 10 Webhooks or Messages, please make thoughful posts', delete_after=15.0)

      channels.append(channel.id)

  @client.event
  async def on_member_join(member):
    U = User(member, server.nicks[-1] + 1)
    server.add((U.member, U.ID, U.nick))
    await member.edit(nick=server.nicks[server.members.index(member)])

  @client.command()
  async def delete(ctx):
    for c in channels:
      d = await client.fetch_channel(c)
      await d.delete()

  @client.command(pass_context=True)
  async def chnick(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)

  @client.command()
  async def answer(ctx):
    await ctx.send("hello")

  client.run()


run(TOKEN)