

# import file_manager
# file_manager.create_map("2200")
# import discord
# import asyncio
# from discord.ext.commands import Bot
# from discord.ext.commands import Bot, has_permissions, CheckFailure
#
#
# client = Bot(description="My Cool Bot", command_prefix=";")
#
#
# @client.event
# async def on_ready():
#     print("Bot is ready!")
#
#
# @client.command(pass_context=True)
# @has_permissions(administrator=False)
# async def whoami(ctx):
#     msg = "You're an admin {}".format(ctx.message.author.mention)
#     await ctx.send(msg)
#
#
# @whoami.error
# async def whoami_error(ctx, error):
#     print("error", error, ctx)
#     if isinstance(error, CheckFailure):
#         msg = "You're an average joe {}".format(ctx.message.author.mention)
#         await ctx.send(msg)
#     else:
#         raise
#
#
# client.run("ODExNjA4ODgzNjU0ODE5ODYw.YC0rrA.aXpHWRUd1QrE_8bU50p0pDYA1lI")
