import asyncio
import praw
import time
import discord
from discord.ext import commands, tasks

# Reddit API credentials
CLIENT_ID = 'I8ZjdD8GCD9tj4eD6A8zeQ'
CLIENT_SECRET = 'XnArdz5kolYJhmc-Ay8MY0dXK4En2w'
USER_AGENT = 'SANDER_11'

# Discord API credentials
DISCORD_TOKEN = 'MTExMTQ4OTEyMTQ0NjI4MTI0Nw.GVRTEc.-KCFgaDTd12kyDSHgUfFxJ9QpQxbOXl_yB8JrY'
GUILD_ID = '1110262781632053322'
CHANNEL_ID = '1110262782131191872'

# Subreddit to monitor
SUBREDDIT = 'buildapcsales'

FILTERS_FILE = 'filters.txt'

# Create a Reddit instance
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

# Create a Discord client
client = discord.Client(intents=discord.Intents.default())

# Set the initial time
last_check_time = time.time()

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


def load_filters():
    try:
        with open(FILTERS_FILE, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        return []


def save_filters():
    with open(FILTERS_FILE, 'w') as file:
        file.write('\n'.join(filters))


filters = load_filters()


def add_user_filter(new_filter):
    added = False
    if new_filter.lower() not in filters:
        filters.append(new_filter.lower())
        save_filters()
        added = True
    return added


def remove_user_filter(user_filter):
    removed = False
    if user_filter.lower() in filters:
        filters.remove(user_filter.lower())
        save_filters()
        removed = True
    return removed


@bot.command(name='add', help='Add one or more filters to the list.')
async def add_filter(ctx, *user_filters):
    for filter in user_filters:
        if add_user_filter(filter):
            await ctx.send(f'Added "{filter}" to the list of filters.')
        else:
            await ctx.send(f'The filter: "{filter}" was already in the list.')


@bot.command(name='rm', help='Remove one or more filters from the list.')
async def remove_filter(ctx, *user_filters):
    for user_filter in user_filters:
        if remove_user_filter(user_filter):
            await ctx.send(f'Removed "{user_filter}" from the list of filters.')
        else:
            await ctx.send(f'The filter: "{user_filter}" was not in the list.')


@bot.command(name='list', help='List the current filters.')
async def list_filters(ctx):
    if len(filters) > 0:
        await ctx.send(', '.join(filters))
    else:
        await ctx.send('Filter list empty.')


@client.event
async def on_ready():
    print('Logged in as', client.user.name)
    print('------')
    await monitor_subreddit()


@bot.command(name='check', help='Check the subreddit now.')
async def check_now(ctx):
    subreddit = reddit.subreddit(SUBREDDIT)
    new_posts = subreddit.new(limit=20)
    found = False
    for post in new_posts:
        if any(filter in post.title.lower() for filter in filters):
            message = f"New post found!\nTitle: {post.title}\nLink: {post.url}"
            found = True
            await ctx.send(message)
    if not found:
        await ctx.send('No posts found matching filters.')


# Continuously monitor the subreddit
@tasks.loop(seconds=10)
async def monitor_subreddit():
    print('safdea')
    await bot.wait_until_ready()
    guild = bot.get_guild(int(GUILD_ID))
    channel = guild.get_channel(int(CHANNEL_ID))
    while not bot.is_closed():
        print('Checking reddit...')
        # Get the latest posts from the subreddit
        subreddit = reddit.subreddit(SUBREDDIT)
        new_posts = subreddit.new(limit=20)

        # Check each new post
        for post in new_posts:
            post_time = post.created_utc

            # If the post is newer than the last check time and matches any of the filters, post a message
            if post_time > last_check_time and any(
                    filter_text.lower() in post.title.lower() for filter_text in filters):
                message = f"New post found!\nTitle: {post.title}\nLink: {post.url}"
                await channel.send(message)

        # Update the last check time
        last_check_time = time.time()
bot.run(DISCORD_TOKEN)
asyncio.run(monitor_subreddit())

