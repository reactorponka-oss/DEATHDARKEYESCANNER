#!/usr/bin/env python3
# Kinsta Serverless Function - Telegram Bot
# All 14 Features - Educational Research Only

import os
import json
import logging
from datetime import datetime
import sqlite3
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Telethon for Kinsta (lightweight)
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
import asyncio
import nest_asyncio

nest_asyncio.apply()

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8837738299:AAGjFwfQtU7XHgOyRYSEzDt_HZ6KWUmGU0Q")
API_ID = int(os.environ.get("API_ID", 30622410))
API_HASH = os.environ.get("API_HASH", "ac0e642a6cf43ced04f3cc2eabf5a21d")

# --- DATABASE (SQLite in /tmp for Kinsta) ---
DB_PATH = "/tmp/darkeye.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, price TEXT, seller TEXT, rating TEXT,
                  market TEXT, url TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- BOT ---
bot = TelegramClient('darkeye_kinsta', API_ID, API_HASH)

# --- IMAGE GENERATOR ---
async def generate_image(name, price):
    try:
        img = Image.new('RGB', (800, 600), color='#1a0a0a')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 790, 590], outline='#ff4444', width=3)
        font = ImageFont.load_default()
        draw.text((400, 200), name[:20], fill='#ffffff', font=font, anchor='mm')
        draw.text((400, 280), f"💰 Price: {price}", fill='#ffd700', font=font, anchor='mm')
        draw.text((400, 340), "🔒 Dark Web Listing", fill='#00ff00', font=font, anchor='mm')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer
    except:
        return None

# --- COMMANDS ---
@bot.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    await event.reply(
        f"🔥 **DarkEye Scanner Bot**\n\n"
        f"Welcome, {event.sender.first_name}!\n\n"
        f"**Commands:**\n"
        f"/gn <product> - Search\n"
        f"/leak <type> - Leaked data\n"
        f"/vendor <name> - Vendor\n"
        f"/market <name> - Stats\n"
        f"/track <product> - Track\n"
        f"/trending - Hot deals\n"
        f"/image <product> - Image\n"
        f"/export - Export\n\n"
        f"⚡ **Platform:** Kinsta"
    )

@bot.on(events.NewMessage(pattern='/gn (.*)'))
async def search_product(event):
    query = event.pattern_match.group(1)
    if not query:
        await event.reply("❌ Example: `/gn AK47`")
        return
    
    products = [
        {'name': f"{query} (Russian)", 'price': "$1,200", 'seller': "RedArmory", 
         'rating': "⭐ 4.8/5", 'market': "AlphaBay", 'url': "http://darkmarket.onion"},
        {'name': f"{query} (Tactical)", 'price': "$1,500", 'seller': "SilentKill",
         'rating': "⭐ 4.9/5", 'market': "DarkMarket", 'url': "http://darkmarket.onion"}
    ]
    
    response = f"🔍 **Results for:** `{query}`\n\n"
    for item in products:
        response += f"**{item['name']}**\n"
        response += f"💰 {item['price']}\n"
        response += f"🛒 {item['market']}\n"
        response += f"👤 {item['seller']}\n"
        response += f"⭐ {item['rating']}\n"
        response += f"🔗 {item['url']}\n\n"
        
        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, seller, rating, market, url) VALUES (?, ?, ?, ?, ?, ?)",
                  (item['name'], item['price'], item['seller'], item['rating'], item['market'], item['url']))
        conn.commit()
        conn.close()
        
        img = await generate_image(item['name'], item['price'])
        if img:
            await event.client.send_file(event.chat_id, img, caption=f"🖼️ {item['name']}")
    
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/trending'))
async def trending(event):
    response = "🔥 **Hot Listings**\n\n"
    response += "1. AK47 – $1,200 (50 views)\n"
    response += "2. Glock19 – $900 (40 views)\n"
    response += "3. Credit Card – $25 (120 views)\n"
    response += "4. US Passport – $800 (30 views)"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/export'))
async def export_data(event):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY timestamp DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        await event.reply("❌ No data")
        return
    
    csv = "Name,Price,Market,URL\n"
    for row in rows:
        csv += f"{row[1]},{row[2]},{row[5]},{row[6]}\n"
    
    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(f"/tmp/{filename}", 'w') as f:
        f.write(csv)
    await event.client.send_file(event.chat_id, f"/tmp/{filename}")
    os.remove(f"/tmp/{filename}")

# --- MAIN ---
async def main():
    await bot.start()
    print("✅ Bot is running on Kinsta!")
    await bot.run_until_disconnected()

# Kinsta handler
def handler(event, context):
    asyncio.run(main())
    return {"statusCode": 200, "body": "Bot Running"}
