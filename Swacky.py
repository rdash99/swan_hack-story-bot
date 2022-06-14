import discord
from datetime import datetime
import os
import pandas as pd
from fpdf import FPDF
import random


client = discord.Client()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # channel id for the sandbox channel
    channel = client.get_channel(519591466058907669)
    # async with channel.typing():
    # await channel.send('Hello, I am Swacky!')
    # await channel.send('Any messages sent in this channel after this message which are not from bots will be stored in a log file, this includes messages which are just a single emoji, or a single word.')
    # await channel.send('Please do not send any messages which contain custom emojis as this can cause issues when generating the output pdf.')
    # await channel.send('Only your first message will end up in the output PDF, any other messages will be ignored.')


@client.event
async def on_message(message):

    if message.author.bot:
        return

    if message.author == client.user:
        return

    if message.content.startswith('#swack process_log'):
        async with message.channel.typing():
            processLog()
        await message.reply("Processed Log")
        await message.reply(file=discord.File('Swack.pdf'))
        # await message.reply(file=discord.File('log.csv'))
        return

    if not isinstance(message.channel, discord.DMChannel):
        log(message)


def log(message):
    createFile()
    data = pd.DataFrame(columns=['content', 'author', 'timestamp', 'id'])
    if message.content.startswith('$log'):
        print(message.content)

    try:
        df = pd.read_csv('log.csv')
    except:
        pass

    data = df.append({'content': message.content, 'author': message.author.nick,
                      'timestamp': message.created_at, 'id': message.author.id}, ignore_index=True)

    # Remove emojis from the messages only
    data['content'] = data['content'].apply(lambda x: x.encode(
        'ascii', 'ignore').decode('ascii'))

    # Remove double spaces from the messages
    data['content'] = data['content'].str.replace(' {2,}', ' ', regex=True)

    data.to_csv('log.csv', index=False)


def createFile():
    if not os.path.exists('log.csv'):
        with open('log.csv', 'w') as f:
            f.write('content,author,timestamp\n')


def processLog():
    df = pd.read_csv('log.csv')

    authors = []
    strings = []
    ids = []
    # store the author and message content in a text file, each author is only allowed to have one message per day
    for i in range(len(df)):
        if not ids.__contains__(df.iloc[i]['id']):
            ids.append(df.iloc[i]['id'])
            authors.append(df.iloc[i]['author'])
            strings.append(df.iloc[i]['content'])

    print(authors)
    print(strings)

    pdf = FPDF()

    pdf.add_page()

    # set style and size of font
    pdf.set_font("Arial", size=15)

    random.shuffle(authors)

    contributors = "Contributors: "

    outString = ""
    for i in range(len(authors)):
        outString += strings[i] + ". "
        if i == len(authors)-1:
            contributors += authors[i]
        else:
            contributors += authors[i] + ", "
    outString += " \n"

    pdf.multi_cell(200, 10, txt=outString,
                   align='L')

    pdf.multi_cell(200, 10, txt=contributors,
                   align='L')

    pdf.image(name='swan_hack_logo.png', w=25, h=25)

    # save the pdf
    pdf.output("Swack.pdf")


def getToken():
    token = ""
    with open('token.txt', 'r') as f:
        token = f.read()
    return token


client.run(getToken())
