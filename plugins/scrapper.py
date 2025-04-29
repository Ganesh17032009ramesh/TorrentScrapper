import os
import aiohttp
import asyncio
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pyrogram import Client, filters
from plugins.messages import caption

# Chrome driver setup with environment validation
options = webdriver.ChromeOptions()

chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

if not chrome_bin or not chromedriver_path:
    raise EnvironmentError("GOOGLE_CHROME_BIN or CHROMEDRIVER_PATH is not set properly.")

options.binary_location = chrome_bin
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")

driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
driver.maximize_window()
torrent = []


@Client.on_message(filters.regex("index\.php\?/forums/topic"))
async def link_regex(c, m):
    try:
        link = str(m.text)
        txt = await m.reply_text("Scraping torrent link, Please Wait")
        driver.get(link)
        p = driver.find_element(By.CLASS_NAME, "ipsImage_thumbnailed").get_attribute("src")
        torrent_link = driver.find_elements(By.CLASS_NAME, "ipsAttachLink_block")

        try:
            title = driver.find_element(By.XPATH, '//h1').text
        except NoSuchElementException:
            title = ""
        heading = f"**{title}**\n\n"
        msg = ""

        for link in torrent_link:
            tor = link.get_attribute("href")
            text = link.text
            msg += f"**Name : {text}**\n**Link:** {tor}\n\n-\n\n"

        if not msg:
            await c.send_message(-1001549256479, "No Torrents Found")
        else:
            await c.send_photo(-1001549256479, p, caption=heading)
            await c.send_message(-1001549256479, msg)

        await txt.delete()

    except Exception as e:
        print(e)
        await c.send_message(-1001549256479, 'Some error occurred')
        await txt.delete()


@Client.on_message(filters.command('listmv'))
async def listmv(c, m):
    querys = " ".join(m.command[1:])
    if not querys:
        return await m.reply('`/listmv [query]`', quote=True)

    link = f"https://www.1tamilmv.com/index.php?/search/&q={querys}&search_and_or=and&search_in=titles&sortby=relevancy"
    txt = await m.reply_text(f"Searching for: {querys} 🔍")
    driver.get(link)
    await asyncio.sleep(5)
    title = driver.title
    links = driver.find_elements(By.CLASS_NAME, "ipsStreamItem_title")

    texts = ""
    for count, link in enumerate(links[:20], 1):
        text = link.text
        url = link.find_element(By.CLASS_NAME, 'ipsType_break').find_element(By.TAG_NAME, 'a').get_attribute("href")
        texts += f"{count}. <a href='{url}'>{text}</a>\n\n"

    reply = f"<b>{title}</b>\n\n{texts}"
    await c.send_message(m.chat.id, reply, disable_web_page_preview=True, parse_mode="html")
    await txt.delete()


@Client.on_message(filters.command('listbl'))
async def lists(c, m):
    querys = " ".join(m.command[1:])
    if not querys:
        return await m.reply('`/listbl [query]`', quote=True)

    link = f"https://www.tamilblasters.com/index.php?/search/&q={querys}&search_and_or=and&search_in=titles&sortby=relevancy"
    txt = await m.reply_text(f"Searching for: {querys} 🔍")
    driver.get(link)
    await asyncio.sleep(5)
    title = driver.title
    links = driver.find_elements(By.TAG_NAME, "h2")

    texts = ""
    count = 0
    for link in links[:20]:
        try:
            text = link.text
            url = driver.find_element(By.LINK_TEXT, text).get_attribute("href")
            count += 1
            texts += f"{count}. [{text}]({url})\n\n"
        except NoSuchElementException:
            continue

    reply = f"**{title}**\n\n{texts}"
    await c.send_message(m.chat.id, reply, disable_web_page_preview=True)
    await txt.delete()


@Client.on_message(filters.command('latest'))
async def ss(bot, message):
    txt = await bot.send_message(message.chat.id, "Getting screenshot of latest movies of 1TamilMv.com")
    name1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7)) + ".png"
    driver.get("https://www.1tamilmv.com/")
    driver.save_screenshot(name1)

    name2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7)) + ".png"
    driver.get("https://www.tamilblasters.com/")
    await txt.edit("Got Screenshot of 1TamilMv.com. Now Getting screenshot of latest movies of TamilBlasters.com")
    driver.save_screenshot(name2)

    await txt.delete()
    await message.reply_photo(name1, quote=True, caption="**Screenshot of latest movies of 1TamilMV.com**")
    await message.reply_photo(name2, quote=True, caption="**Screenshot of latest movies of TamilBlasters.com**")

    os.remove(name1)
    os.remove(name2)


@Client.on_message(filters.command('post'))
async def post(bot, message):
    try:
        link = message.reply_to_message.text if message.reply_to_message else None
        if not link and len(message.command) > 1:
            link = message.command[1]
        if not link:
            return await message.reply('`/post [movie_url]`', quote=True)

        txt = await message.reply_text("Loading 🔄", quote=True)
        driver.get(link)
        photo = driver.find_element(By.CLASS_NAME, "ipsImage_thumbnailed").get_attribute("src")

        try:
            title = driver.find_element(By.XPATH, '//h1').text
        except NoSuchElementException:
            title = ""

        heading = f"**{title}**\n"
        await message.reply_photo(photo, caption=heading + caption, quote=True)
        await txt.delete()

    except Exception as e:
        print(e)
        await txt.edit("Some Error Occurred, Try Again")
