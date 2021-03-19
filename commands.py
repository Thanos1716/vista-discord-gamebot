from typing import Union
import discord
from discord.ext.commands import *
import json
import file_manager
from file_manager import exec_sql


# noinspection PyUnusedLocal
def get_prefix(client, ctx):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(ctx.guild.id)]


bot = Bot(command_prefix=get_prefix)

objects = []


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (Name: {guild.name})")
        guild_count += 1
    print(f"{bot.user.display_name} is in {str(guild_count)} guild" + ("." if guild_count == 1 else "s."))


@bot.event
async def on_guild_join(guild):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = ";"

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    del prefixes[str(guild.id)]

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)


class General(Cog):
    @command(aliases=["e"])
    async def emojis(self, ctx):
        emojis_list = ""
        for emoji in ctx.guild.emojis:
            for i in range(2):
                if emoji.animated:
                    emojis_list += "<a:"
                else:
                    emojis_list += "<:"
                emojis_list += emoji.name + ":" + str(emoji.id) + ">"
                if i == 0:
                    emojis_list += ": "
                emojis_list += "`"
            emojis_list += "\n"
        await ctx.send(embed=discord.Embed(title="Emojis:", description=emojis_list, colour=0xDDDD00))


class Game(Cog):
    @command(aliases=["i"])
    async def inventory(self, ctx, target: Union[discord.Member, str, None], *, item: str = None):

        # If author doesn't another player, add the target field to the item field and set the target player to author
        if not isinstance(target, discord.Member):
            if target and (item is None):
                item = target
            elif target and item:
                item = f"{target} {item}"
            target = ctx.author

        # If item field exists, if found, send item as embed otherwise send item not found embed
        if item:
            found = False
            for o in objects:
                if o.location == str(target.id) and o.name == item:
                    await ctx.send(embed=o.embed_item())
                    found = True
                    break
            if not found:
                await ctx.send(
                    embed=discord.Embed(title="Item Not Found",
                                        description="The item {} is not in {} inventory".format(
                                            item, target.display_name + "'s" if target != ctx.author else "your"),
                                        colour=0xFF8800))

        # Otherwise, send full target inventory embed
        else:
            found = False
            for p in objects:
                if p.object_class == "players" and p.class_id == target.id:
                    await ctx.send(embed=discord.Embed(
                        title=("Your" if p.class_id == target.id else p.name + "'s") + " Inventory",
                        description=p.embed_contents(), colour=0xFF8800))
                    found = True
            if not found:
                await ctx.send(embed=discord.Embed(
                    title="Search by ID",
                    description="Currently not supported, please use `@[target]` instead", colour=0xFF8800))


    @command(aliases=["m"])
    async def map(self, ctx, seed: str = None):
        if seed:
            seed = seed[:4]
            try:
                file = discord.File(f"saves/{file_manager.savename}/{seed}.png")
            except FileNotFoundError:
                await ctx.send(embed=discord.Embed(title="Generating Map...", colour=0x001A67))
                file_manager.create_map(seed)
                file = discord.File(f"saves/{file_manager.savename}/{seed}.png")
            e = discord.Embed(colour=0x001A67)
            e.set_image(url=f"attachment://{seed}.png")
            await ctx.send(file=file, embed=e)
        else:
            await ctx.send(embed=discord.Embed(title="Missing argument",
                                               description=f"Correct usage: `{get_prefix(bot, ctx)}map [seed]`",
                                               colour=0xBB0000))

    @command()
    async def players(self, ctx):
        out = ""
        print(objects)
        for p in objects:
            if p.object_class == "players":
                out += p.name + "\n"
        await ctx.send(embed=discord.Embed(title="Players", description=out, colour=0x0033FF))


class Admin(Cog):
    @command(aliases=['p'])
    @has_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix: str = None):
        if new_prefix:
            with open("prefixes.json", 'r') as f:
                prefixes = json.load(f)
            if prefixes[str(ctx.guild.id)] != new_prefix:
                prefixes[str(ctx.guild.id)] = new_prefix

                with open("prefixes.json", 'w') as f:
                    json.dump(prefixes, f, indent=4)

                await ctx.send(embed=discord.Embed(title="Command Prefix Updated",
                                                   description=f"{ctx.author.mention} has changed {bot.user.mention}'s "
                                                               f"command prefix to '{new_prefix}'",
                                                   colour=0xFFFFFE))
            else:
                await ctx.send(embed=discord.Embed(title="Command Prefix Reassignment",
                                                   description=f"{bot.user.mention}'s command prefix is already "
                                                               f"'{new_prefix}'",
                                                   colour=0xBB0000))
        else:
            await ctx.send(embed=discord.Embed(title="Missing Argument",
                                               description=f"Correct usage: `{get_prefix(bot, ctx)}prefix "
                                                           f"[new_prefix]`",
                                               colour=0xBB0000))

    @prefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(embed=discord.Embed(title="Permission Denied",
                                               description="You do not have administrator permissions",
                                               colour=0xBB0000))
        else:
            raise

    @command()
    @is_owner()
    async def sql(self, ctx, *, code):
        await ctx.send(embed=discord.Embed(title="Output:", description=str(
            exec_sql("datapacks/default_datapack/default_items.db", code)), colour=0xFFFFFE))

    @sql.error
    async def sql_error(self, ctx, error):
        if isinstance(error, NotOwner):
            await ctx.send(embed=discord.Embed(title="Permission Denied",
                                               description="You must be the owner of this bot to use this command",
                                               colour=0xBB0000))
        else:
            raise


class Help(MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            help_embed = discord.Embed(title="Help:", description=page, colour=0x3388DD)
            await destination.send(embed=help_embed)


bot.help_command = Help()
