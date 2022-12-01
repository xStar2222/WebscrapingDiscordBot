import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from discord_webhook import DiscordWebhook, DiscordEmbed
import time

url = 'https://www.dictionary.com/e/word-of-the-day/'
html_content = requests.get(url).text
reqs = requests.get(url)
soup = BeautifulSoup(html_content, "html.parser")



text = soup.get_text()

#database
conn = sqlite3.connect('word.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS inmate (name text)")
conn.commit()
conn.close()




with open("settings.json", "r") as f:
    settings = json.load(f)


def main():

    word = soup.find(class_='otd-content wotd-content')

    date = word.find(class_='otd-item-headword__date').text

    wotd = word.find(class_='js-fit-text').text.capitalize()

    type = word.find(class_='luna-pos').text.capitalize()
    

    defa = word.find('p').next_sibling.next_sibling.text.strip().capitalize()




    conn = sqlite3.connect('word.db')
    c = conn.cursor()
    c.execute("SELECT * FROM inmate")
    last_inmate = c.fetchone()
    conn.close()


    #Check if theres a last inmate, if not, create one and send to discord
    if last_inmate == None:
        conn = sqlite3.connect('word.db')
        c = conn.cursor()
        c.execute("INSERT INTO inmate VALUES (?)", (wotd,))
        conn.commit()
        conn.close()


        webhook = DiscordWebhook(url=settings['discordWebhook'])
        embed = DiscordEmbed()
        embed = DiscordEmbed()
        embed.set_title("**New Word Of The Day! 🎉**")
        embed.set_description(f"**The Word Of The Day Is: ** {wotd} **Date:** {date}\n\n **Type:** {type}\n\n **Definition**: {defa}")
        embed.set_timestamp()
        embed.set_color(0xFFFFFF)    
        webhook.add_embed(embed)
        response = webhook.execute()
        print('New inmate detected! Posting to discord')
        return


    #If last inmate is not the same as the current inmate, update the database and post to discord
    elif last_inmate[0] != word:

        conn = sqlite3.connect('word.db')
        c = conn.cursor()
        c.execute("UPDATE inmate SET name = (?)", (wotd,))
        conn.commit()
        conn.close()

        webhook = DiscordWebhook(url=settings['discordWebhook'])
        embed = DiscordEmbed()
        embed = DiscordEmbed()
        embed.set_title("**New Word Of The Day! 🎉**")
        embed.set_description(f"**The Word Of The Day Is: ** {wotd}\n\n **Date:**{date}\n\n **Type:** {type}\n\n **Definition**: {defa}")
        embed.set_timestamp()
        embed.set_color(0xFFFFFF)    

        webhook.add_embed(embed)
        response = webhook.execute()

        print('New inmate detected! Posting to discord')
        return
    
    else:
        print("Latest inmate is the same, sleeping for 1 minute...")
        return	



if __name__ == "__main__":
    print('\nStarting Inmates Monitor...')
    print()
    while True:
        main()
        time.sleep(60)