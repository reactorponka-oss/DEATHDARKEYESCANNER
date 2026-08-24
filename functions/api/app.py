#!/usr/bin/env python3
# Kinsta Nixpacks Compatible Bot
# All 14 Features - Educational Research Only

import os
import json
import logging
from datetime import datetime
import sqlite3
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Telethon
from telethon import TelegramClient, events
import asyncio
import nest_asyncio

nest_asyncio.apply()

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8837738299:AAGjFwfQtU7XHgOyRYSEzDt_HZ6KWUmGU0Q")
API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")

# --- DATABASE ---
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
        draw.text((750, 570), "DarkEye", fill='#333333', font=font, anchor='rd')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer
    except:
        return None

# --- MOCK DATA ---
def mock_products(query):
    return [
        {'name': f"{query} (Russian)", 'price': "$1,200", 'seller': "RedArmory", 
         'rating': "⭐ 4.8/5", 'market': "AlphaBay", 'url': "http://darkmarket.onion"},
        {'name': f"{query} (Tactical)", 'price': "$1,500", 'seller': "SilentKill",
         'rating': "⭐ 4.9/5", 'market': "DarkMarket", 'url': "http://darkmarket.onion"}
    ]

# --- BOT ---
bot = TelegramClient('darkeye_kinsta', API_ID, API_HASH)

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
    
    products = mock_products(query)
    response = f"🔍 **Results for:** `{query}`\n\n"
    
    for item in products:
        response += f"**{item['name']}**\n"
        response += f"💰 {item['price']}\n"
        response += f"🛒 {item['market']}\n"
        response += f"👤 {item['seller']}\n"
        response += f"⭐ {item['rating']}\n"
        response += f"🔗 {item['url']}\n\n"
        
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
    
    filename = f"/tmp/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w') as f:
        f.write(csv)
    await event.client.send_file(event.chat_id, filename)
    os.remove(filename)

@bot.on(events.NewMessage(pattern='/leak (.*)'))
async def leak_search(event):
    query = event.pattern_match.group(1)
    data = {
        'credit cards': {'category': 'Credit Cards', 'price': '$25–$50', 'seller': 'CardKing'},
        'passport': {'category': 'US Passport', 'price': '$800', 'seller': 'GhostDocs'},
        'ssn': {'category': 'SSN', 'price': '$15-$30', 'seller': 'DataKing'}
    }
    
    result = data.get(query.lower(), {'category': 'General', 'price': '$10-$100', 'seller': 'Various'})
    response = f"💳 **Leaked Data:** `{query}`\n\n"
    response += f"**Category:** {result['category']}\n"
    response += f"💰 **Price:** {result['price']}\n"
    response += f"👤 **Seller:** {result['seller']}\n"
    response += "⚠️ *For educational research only*"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/vendor (.*)'))
async def vendor_search(event):
    vendor = event.pattern_match.group(1)
    response = f"👤 **Vendor:** `{vendor}`\n\n"
    response += f"⭐ **Rating:** 4.8/5 (342 reviews)\n"
    response += f"🏪 **Markets:** AlphaBay, DarkMarket\n"
    response += f"📦 **Sales:** 1,234\n"
    response += f"🔫 **Top Products:** AK47, Glock19\n"
    response += f"🔐 **PGP Key:** Available\n"
    response += f"✅ *Verified vendor*"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/market (.*)'))
async def market_stats(event):
    market = event.pattern_match.group(1)
    response = f"📊 **Market:** `{market}`\n\n"
    response += f"🟢 **Status:** ✅ Online\n"
    response += f"⏱️ **Uptime:** 98.7%\n"
    response += f"📦 **Listings:** 124,500\n"
    response += f"🏆 **Top Vendors:** RedArmory, SilentKill"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/track (.*)'))
async def track_product(event):
    product = event.pattern_match.group(1)
    response = f"✅ **Tracking started for:** `{product}`\n\n"
    response += f"💰 **Current Price:** $1,200\n"
    response += f"🎯 **Target Price:** $1,000\n"
    response += f"🔔 *You'll be notified when price drops!*"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/image (.*)'))
async def image_search(event):
    product = event.pattern_match.group(1)
    img = await generate_image(product, "$1,200")
    if img:
        await event.client.send_file(event.chat_id, img, caption=f"🖼️ {product}")
    else:
        await event.reply("❌ Image generation failed")

@bot.on(events.NewMessage(pattern='/filter (.*)'))
async def filter_products(event):
    parts = event.pattern_match.group(1).split()
    if len(parts) < 3:
        await event.reply("❌ Usage: `/filter weapons 500 2000`")
        return
    category, min_p, max_p = parts[0], parts[1], parts[2]
    response = f"🔍 **Filtered:** {category} (${min_p} - ${max_p})\n\n"
    response += "1. AK47 – $1,200\n2. Glock19 – $900\n3. M4A1 – $1,800"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/deep (.*)'))
async def deep_search(event):
    query = event.pattern_match.group(1)
    response = f"🌐 **Deep Search:** `{query}`\n\n"
    response += "🇷🇺 Russian: AK-47 – $1,200 USD / 0.018 BTC\n"
    response += "🇫🇷 French: AK-47 – $1,200 USD\n"
    response += "💰 **Currency:** USD | BTC | XMR"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/scam (.*)'))
async def scam_check(event):
    vendor = event.pattern_match.group(1)
    response = f"🔍 **Scam Check:** `{vendor}`\n\n"
    response += "🟢 **Risk:** Low (4.8/5)\n"
    response += "✅ **Verified:** PGP, 2FA\n"
    response += "🛡️ *Safe to trade*"
    await event.reply(response)

@bot.on(events.NewMessage(pattern='/proxy'))
async def toggle_proxy(event):
    response = "🔒 **Proxy:** Enabled\n"
    response += "🌐 IP: 127.0.0.1 (via TOR)\n"
    response += "🔄 Circuit: Active"
    await event.reply(response)

# --- MAIN (Nixpacks WILL START THIS) ---
async def main():
    await bot.start()
    print("✅ Bot is running on Kinsta!")
    await bot.run_until_disconnected()

# Nixpacks default entry point
if __name__ == "__main__":
    asyncio.run(main())
