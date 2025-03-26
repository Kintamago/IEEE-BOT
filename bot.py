import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import json
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot with command prefix '<>' and specified intents
bot = commands.Bot(command_prefix='<>', intents=intents)

# Dictionary to store server-specific menu configurations
server_menus = {}

# Load and save menu configurations
def load_menus():
    try:
        with open('server_menus.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_menus():
    with open('server_menus.json', 'w') as f:
        json.dump(server_menus, f, indent=4)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    global server_menus
    server_menus = load_menus()
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.command(name='ping')
async def ping(ctx):
    """Simple command to check if the bot is responsive."""
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.event
async def on_message(message):
    """Event triggered when a message is sent in a channel the bot can see."""
    if message.author == bot.user:
        return
    # Process commands
    await bot.process_commands(message)

# Basic embed example
@bot.command()
async def info(ctx):
    """Shows how to create a basic embed with title, description, and fields."""
    embed = discord.Embed(
        title="Server Information",
        description="Here's some information about our server!",
        color=discord.Color.blue(),
        type='rich',
        url = 'https://www.youtube.com/'
    )
    
    # Add fields to the embed
    embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
    embed.add_field(name="Member Count", value=ctx.guild.member_count, inline=True)
    embed.add_field(name="Created At", value=ctx.guild.created_at.strftime("%Y-%m-%d"), inline=True)
    
    # Add a thumbnail
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    # Add footer
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Interactive embed with reactions
@bot.command()
async def menu(ctx, menu_name: str = None):
    """Display a custom menu or list available menus if no name provided."""
    server_id = str(ctx.guild.id)
    
    # If no menu name provided, list available menus
    if menu_name is None:
        await list_menus(ctx)
        return
    
    # Check if menu exists
    if server_id not in server_menus or menu_name not in server_menus[server_id]:
        await ctx.send(f"Menu '{menu_name}' not found! Use !list_menus to see available menus.")
        return
    
    menu_data = server_menus[server_id][menu_name]
    
    # Create and send the menu embed
    embed = discord.Embed(
        title=f"Menu: {menu_name}",
        description="React to select an option:",
        color=discord.Color.green()
    )
    
    for emoji, description in menu_data["options"].items():
        embed.add_field(name=emoji, value=description, inline=False)
    
    # Send embed and add reactions
    message = await ctx.send(embed=embed)
    for emoji in menu_data["options"].keys():
        await message.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    """Handle menu reactions."""
    if user == bot.user:
        return
        
    message = reaction.message
    if not message.embeds:
        return
        
    embed = message.embeds[0]
    if not embed.title.startswith("Menu: "):
        return
        
    menu_name = embed.title.replace("Menu: ", "")
    server_id = str(message.guild.id)
    
    if (server_id in server_menus and 
        menu_name in server_menus[server_id] and 
        str(reaction.emoji) in server_menus[server_id][menu_name]["options"]):
        
        option_description = server_menus[server_id][menu_name]["options"][str(reaction.emoji)]
        await message.channel.send(f"{user.mention} selected {reaction.emoji}: {option_description}")

# Rich embed example with multiple features
@bot.command()
async def profile(ctx, member: discord.Member = None):
    """Shows a user's profile in a rich embed."""
    member = member or ctx.author
    
    embed = discord.Embed(
        title=f"User Profile - {member.name}",
        description=f"Here's the profile for {member.mention}",
        color=member.color,
        timestamp=datetime.datetime.now()
    )
    
    # Add member information
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.name, inline=True)
    
    # Add status information
    status_emoji = {
        "online": "🟢",
        "idle": "🟡",
        "dnd": "🔴",
        "offline": "⚫"
    }
    embed.add_field(name="Status", value=f"{status_emoji.get(str(member.status), '⚫')} {str(member.status).title()}", inline=True)
    
    # Set thumbnail to user's avatar
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    
    # Add footer with timestamp
    embed.set_footer(text=f"ID: {member.id}")
    
    await ctx.send(embed=embed)

# Progress bar embed example
@bot.command()
async def progress(ctx, percent: int = None):
    """Shows a progress bar in an embed."""
    try:
        # Check if percent was provided
        if percent is None:
            await ctx.send("Please provide a percentage (0-100)!\nUsage: !progress <number>")
            return
            
        # Convert to integer if possible and check range
        percent = int(percent)
        if not 0 <= percent <= 100:
            await ctx.send("Percentage must be between 0 and 100!")
            return
        
        # Create progress bar (each block represents 5%)
        blocks = 20  # Total number of blocks
        filled_blocks = round(percent / 100 * blocks)
        progress_bar = "█" * filled_blocks + "░" * (blocks - filled_blocks)
        
        embed = discord.Embed(
            title="Progress Bar",
            description=f"`{progress_bar}` {percent}%",
            color=discord.Color.purple()
        )
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("Please provide a valid number between 0 and 100!\nUsage: !progress <number>")

# Command to create a custom menu
@bot.command()
@commands.has_permissions(administrator=True)
async def create_menu(ctx, menu_name: str):
    """Create a new custom menu for the server."""
    server_id = str(ctx.guild.id)
    
    if server_id not in server_menus:
        server_menus[server_id] = {}
    
    if menu_name in server_menus[server_id]:
        await ctx.send(f"A menu named '{menu_name}' already exists!")
        return
    
    server_menus[server_id][menu_name] = {"options": {}}
    save_menus()
    
    await ctx.send(f"Created new menu '{menu_name}'. Use !add_option {menu_name} <emoji> <description> to add options!")

# Command to add option to a menu
@bot.command()
@commands.has_permissions(administrator=True)
async def add_option(ctx, menu_name: str, emoji: str, *, description: str):
    """Add an option to a custom menu."""
    server_id = str(ctx.guild.id)
    
    if server_id not in server_menus or menu_name not in server_menus[server_id]:
        await ctx.send(f"Menu '{menu_name}' not found! Create it first with !create_menu {menu_name}")
        return
    
    server_menus[server_id][menu_name]["options"][emoji] = description
    save_menus()
    
    await ctx.send(f"Added option {emoji} to menu '{menu_name}'!")

# Command to remove option from a menu
@bot.command()
@commands.has_permissions(administrator=True)
async def remove_option(ctx, menu_name: str, emoji: str):
    """Remove an option from a custom menu."""
    server_id = str(ctx.guild.id)
    
    if server_id not in server_menus or menu_name not in server_menus[server_id]:
        await ctx.send(f"Menu '{menu_name}' not found!")
        return
    
    if emoji in server_menus[server_id][menu_name]["options"]:
        del server_menus[server_id][menu_name]["options"][emoji]
        save_menus()
        await ctx.send(f"Removed option {emoji} from menu '{menu_name}'!")
    else:
        await ctx.send(f"Option {emoji} not found in menu '{menu_name}'!")

# Command to list all menus
@bot.command()
async def list_menus(ctx):
    """List all custom menus for this server."""
    server_id = str(ctx.guild.id)
    
    if server_id not in server_menus or not server_menus[server_id]:
        await ctx.send("No custom menus found for this server!")
        return
    
    embed = discord.Embed(
        title="Custom Menus",
        description="Here are all the custom menus for this server:",
        color=discord.Color.blue()
    )
    
    for menu_name, menu_data in server_menus[server_id].items():
        options_text = "\n".join([f"{emoji} : {desc}" for emoji, desc in menu_data["options"].items()])
        embed.add_field(name=menu_name, value=options_text or "No options added", inline=False)
    
    await ctx.send(embed=embed)

def main():
    """Main function to run the bot."""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No token found! Make sure to set DISCORD_TOKEN in .env file")
    
    bot.run(token)

if __name__ == "__main__":
    main() 