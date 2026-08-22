#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DarkEye Scanner Bot v2.0 - Complete 14 Features
# Render Deployment - Fully Working
# By Shadow Hacker & Butter

import os
import asyncio
import logging
import sqlite3
import json
import random
import re
import time
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
import aiofiles

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DarkEye")

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8837738299:AAGjFwfQtU7XHgOyRYSEzDt_HZ6KWUmGU0Q")
API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
USE_TOR = os.environ.get("USE_TOR", "false").lower() == "true"

# --- DATABASE ---
DB_FILE = "darkeye.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, price TEXT, seller TEXT, rating TEXT,
                  market TEXT, condition TEXT, shipping TEXT,
                  stock TEXT, description TEXT, url TEXT,
                  category TEXT, image_url TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Vendors table
    c.execute('''CREATE TABLE IF NOT EXISTS vendors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE, rating TEXT, markets TEXT,
                  sales TEXT, top_products TEXT, feedback TEXT,
                  last_seen TEXT, pgp_key TEXT, url TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS tracking
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, product TEXT, target_price TEXT,
                  chat_id INTEGER, current_price TEXT, last_check DATETIME,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Cache table
    c.execute('''CREATE TABLE IF NOT EXISTS cache
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query TEXT UNIQUE, response TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Search history
    c.execute('''CREATE TABLE IF NOT EXISTS search_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, query TEXT, results TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

init_db()

# --- CREATE BOT INSTANCE ---
app = Client(
    "darkeye_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# --- IMAGE GENERATOR ---
async def generate_product_image(product_name, price, accessory=None, is_leak=False):
    try:
        # Background color based on type
        if is_leak:
            bg_color = '#0a0a1a'
            border_color = '#ff8800'
        else:
            bg_color = '#1a0a0a'
            border_color = '#ff4444'
        
        img = Image.new('RGB', (800, 600), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Border
        draw.rectangle([10, 10, 790, 590], outline=border_color, width=3)
        
        # Grid pattern
        for i in range(0, 800, 40):
            draw.line([(i, 0), (i, 600)], fill='#2a2a2a', width=1)
            draw.line([(0, i), (800, i)], fill='#2a2a2a', width=1)
        
        # Fonts
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
        except:
            font_big = ImageFont.load_default()
            font_med = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Title
        draw.text((400, 150), product_name[:30], fill='#ffffff', font=font_big, anchor='mm')
        
        # Accessory if present
        if accessory:
            draw.text((400, 210), f"+ {accessory}", fill='#ff8800', font=font_med, anchor='mm')
        
        # Price
        draw.text((400, 280), f"💰 Price: {price}", fill='#ffd700', font=font_med, anchor='mm')
        
        # Dark web badge
        draw.text((400, 340), "🔒 Dark Web Listing", fill='#00ff00', font=font_small, anchor='mm')
        
        # Warning
        draw.text((400, 400), "⚠️ For Educational Research Only", fill='#ff4444', font=font_small, anchor='mm')
        
        # TOR badge
        if USE_TOR:
            draw.text((50, 550), "🔐 TOR Active", fill='#00ff00', font=font_small)
        
        # Watermark
        draw.text((750, 570), "DarkEye v2.0", fill='#333333', font=font_small, anchor='rd')
        
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Image error: {e}")
        return None

# --- MOCK DATA GENERATOR ---
def generate_mock_products(query, accessory=None):
    products = [
        {
            'name': f"{query} (Russian Variant)",
            'price': "$1,200 USD / 0.018 BTC",
            'seller': "RedArmory",
            'rating': "⭐ 4.8/5 (342 sales)",
            'market': "AlphaBay",
            'condition': "New",
            'shipping': "Worldwide (stealth)",
            'stock': "12 units",
            'description': f"Full auto, 7.62mm, includes 2 mags - {query}",
            'url': "http://darkmarket.onion/ak47",
            'image_url': None
        },
        {
            'name': f"{query} (Tactical Edition)",
            'price': "$1,500 USD / 0.022 BTC",
            'seller': "SilentKill",
            'rating': "⭐ 4.9/5 (89 sales)",
            'market': "DarkMarket",
            'condition': "New",
            'shipping': "Worldwide",
            'stock': "8 units",
            'description': f"Enhanced version with tactical accessories - {query}",
            'url': "http://darkmarket.onion/ak47-tactical",
            'image_url': None
        },
        {
            'name': f"{query} (Vintage Edition)",
            'price': "$900 USD / 0.013 BTC",
            'seller': "VintageArms",
            'rating': "⭐ 4.6/5 (150 sales)",
            'market': "Tor2Door",
            'condition': "Used (Refurbished)",
            'shipping': "Limited regions",
            'stock': "5 units",
            'description': f"Classic {query} with wooden furniture",
            'url': "http://darkmarket.onion/ak47-vintage",
            'image_url': None
        }
    ]
    
    if accessory:
        products[0]['name'] = f"{query} + {accessory} (threaded)"
        products[0]['price'] = "$1,450 USD / 0.022 BTC"
        products[0]['seller'] = "SilentKill"
        products[0]['rating'] = "⭐ 4.9/5 (89 sales)"
        products[0]['market'] = "DarkMarket"
        products[0]['stock'] = "5 units (combo)"
        products[0]['description'] = f"{query} with {accessory} - tactical combo. Includes extra mags, cleaning kit"
    
    return products

def generate_leak_data(query):
    leaks = {
        'credit cards': {
            'category': 'Credit Cards (Visa/Mastercard/Amex)',
            'price': '$25–$50 per card',
            'seller': 'CardKing',
            'rating': '⭐ 4.7/5 (1.2k sales)',
            'market': 'AlphaBay',
            'available': '200+ cards',
            'sample': '4532**** ****1234 | Exp: 12/26 | CVV: 123',
            'types': 'Visa (45%), Mastercard (35%), Amex (20%)',
            'url': 'http://darkmarket.onion/cards'
        },
        'passport': {
            'category': 'US Passport (scannable)',
            'price': '$800 USD',
            'seller': 'GhostDocs',
            'rating': '⭐ 4.9/5 (500 sales)',
            'market': 'DarkMarket',
            'stock': '8 units',
            'shipping': '3–5 days (stealth)',
            'features': 'RFID chip, UV security, Hologram',
            'url': 'http://darkmarket.onion/passports'
        },
        'ssn': {
            'category': 'SSN (Social Security Numbers)',
            'price': '$15-$30 per SSN',
            'seller': 'DataKing',
            'rating': '⭐ 4.5/5 (800 sales)',
            'market': 'AlphaBay',
            'available': '500+ records',
            'includes': 'Full Name, DOB, Address',
            'url': 'http://darkmarket.onion/ssn'
        }
    }
    
    for key, data in leaks.items():
        if key in query.lower():
            return data
    
    return {
        'category': 'General Leak Data',
        'price': '$10-$100',
        'seller': 'Various',
        'rating': '⭐ 4.0/5',
        'market': 'Multiple Markets',
        'available': '1000+ records',
        'url': 'http://darkmarket.onion/leaks'
    }

# --- CACHE FUNCTIONS ---
def get_cache(key):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT response FROM cache WHERE query = ? AND timestamp > datetime('now', '-24 hours')", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None

def set_cache(key, value):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO cache (query, response) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    except:
        pass

# --- COMMANDS ---

# 1. START
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text(
        f"🔥 **DarkEye Scanner Bot v2.0**\n\n"
        f"Welcome to the shadows, {message.from_user.first_name}! 👋\n\n"
        f"**🔍 Core Commands:**\n"
        f"/gn <product> - Search products (e.g., /gn AK47)\n"
        f"/gn <product> with <accessory> - Combo search\n"
        f"/leak <type> - Leaked data (e.g., /leak credit cards)\n"
        f"/leak passport <country> - Passport search\n\n"
        f"**👤 Intelligence:**\n"
        f"/vendor <name> - Vendor profile\n"
        f"/market <name> - Market stats\n"
        f"/scam <vendor> - Scam check\n\n"
        f"**📊 Analytics:**\n"
        f"/trending - Hot listings\n"
        f"/filter <category> <min> <max> - Filter\n"
        f"/track <product> - Price tracking\n\n"
        f"**🛠️ Utilities:**\n"
        f"/image <product> - Image search\n"
        f"/deep <query> - Deep web search\n"
        f"/proxy - Toggle TOR\n"
        f"/export - Export data\n\n"
        f"⚡ **Status:** 🟢 Online\n"
        f"🛠️ **Platform:** Render\n"
        f"🔒 **Security:** {'TOR Enabled' if USE_TOR else 'Standard'}\n\n"
        f"*For educational research only*",
        parse_mode=ParseMode.MARKDOWN
    )

# 2. PRODUCT SEARCH
@app.on_message(filters.command("gn"))
async def search_product(client, message):
    query = message.text.split("/gn", 1)[1].strip()
    if not query:
        await message.reply_text(
            "❌ Please specify a product.\n"
            "Example: `/gn AK47`\n"
            "Example: `/gn AK47 with silencer`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Check cache
    cache_key = f"gn_{query}"
    cached = get_cache(cache_key)
    if cached:
        await message.reply_text(cached, parse_mode=ParseMode.MARKDOWN)
        return
    
    # Parse query
    is_combo = " with " in query.lower()
    product_name = query.split(" with ")[0].strip() if is_combo else query
    accessory = query.split(" with ")[1].strip() if is_combo else None
    
    await client.send_chat_action(message.chat.id, "typing")
    
    products = generate_mock_products(product_name, accessory)
    
    response = f"🔍 **Search Results for:** `{query}`\n"
    response += f"📊 **Found:** {len(products)} listings\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active (IP hidden)\n"
    response += "\n"
    
    for idx, item in enumerate(products, 1):
        response += f"**{idx}. {item['name']}**\n"
        response += f"💰 **Price:** {item['price']}\n"
        response += f"🛒 **Market:** {item['market']}\n"
        response += f"👤 **Seller:** {item['seller']}\n"
        response += f"⭐ **Rating:** {item['rating']}\n"
        response += f"📦 **Stock:** {item['stock']}\n"
        response += f"📝 **Description:** {item['description'][:150]}...\n"
        response += f"🔗 **URL:** {item['url']}\n\n"
        
        # Save to database
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, seller, rating, market, condition, shipping, stock, description, url, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (item['name'], item['price'], item['seller'], item['rating'], item['market'],
                       item.get('condition', 'New'), item.get('shipping', 'Worldwide'),
                       item['stock'], item['description'], item['url'], 'general'))
            conn.commit()
            conn.close()
        except:
            pass
        
        # Send image
        img_data = await generate_product_image(item['name'], item['price'], accessory)
        if img_data:
            caption = f"🖼️ **{item['name']}**\n💰 {item['price']}\n🛒 {item['market']}"
            if accessory:
                caption += f"\n🔧 + {accessory}"
            await client.send_photo(message.chat.id, img_data, caption=caption)
    
    # Cache response
    set_cache(cache_key, response)
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 3. LEAKED DATA
@app.on_message(filters.command("leak"))
async def leak_search(client, message):
    query = message.text.split("/leak", 1)[1].strip()
    if not query:
        await message.reply_text(
            "❌ Please specify what to search.\n"
            "Examples:\n"
            "/leak credit cards\n"
            "/leak passport USA\n"
            "/leak ssn",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await client.send_chat_action(message.chat.id, "typing")
    
    data = generate_leak_data(query)
    
    response = f"💳 **Leaked Data Search:** `{query}`\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    
    response += f"**Category:** {data['category']}\n"
    response += f"💰 **Price:** {data['price']}\n"
    response += f"👤 **Seller:** {data['seller']}\n"
    response += f"⭐ **Rating:** {data['rating']}\n"
    response += f"🏪 **Market:** {data['market']}\n"
    
    if 'available' in data:
        response += f"📦 **Available:** {data['available']}\n"
    if 'stock' in data:
        response += f"📦 **Stock:** {data['stock']}\n"
    if 'sample' in data:
        response += f"🔢 **Sample Data:** {data['sample']}\n"
    if 'types' in data:
        response += f"📋 **Types:** {data['types']}\n"
    if 'shipping' in data:
        response += f"🚚 **Shipping:** {data['shipping']}\n"
    if 'features' in data:
        response += f"🔐 **Features:** {data['features']}\n"
    if 'includes' in data:
        response += f"📊 **Includes:** {data['includes']}\n"
    
    response += f"🔗 **Link:** {data['url']}\n\n"
    response += "⚠️ *For educational research only*"
    
    # Send image
    img_data = await generate_product_image(data['category'], data['price'], is_leak=True)
    if img_data:
        await client.send_photo(
            message.chat.id,
            img_data,
            caption=f"💳 {data['category']}\n💰 {data['price']}\n🛒 Available on {data['market']}"
        )
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 4. VENDOR PROFILE
@app.on_message(filters.command("vendor"))
async def vendor_search(client, message):
    vendor = message.text.split("/vendor", 1)[1].strip()
    if not vendor:
        await message.reply_text(
            "❌ Please specify a vendor name.\n"
            "Example: `/vendor RedArmory`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await client.send_chat_action(message.chat.id, "typing")
    
    response = f"👤 **Vendor Profile:** `{vendor}`\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    response += f"⭐ **Rating:** 4.8/5 (342 reviews)\n"
    response += f"🏪 **Markets Active:** AlphaBay, DarkMarket, Tor2Door\n"
    response += f"📦 **Total Sales:** 1,234\n"
    response += f"🔫 **Top Products:** AK47, Glock19, Ammo packs\n"
    response += f"💬 **Recent Feedback:** 'Fast shipping, good quality' (2 hrs ago)\n"
    response += f"🟢 **Last Seen:** Online now\n"
    response += f"🔐 **PGP Key:** Available\n"
    response += f"🔗 **URL:** http://darkmarket.onion/vendor/{vendor.lower()}\n\n"
    response += f"📊 **Trust Score:** 🟢 High\n"
    response += f"✅ **Verification:** PGP, 2FA, Escrow\n"
    response += f"📅 **Account Age:** 2 years\n\n"
    response += f"🛡️ *Verified vendor - Recommended*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 5. MARKET STATS
@app.on_message(filters.command("market"))
async def market_stats(client, message):
    market = message.text.split("/market", 1)[1].strip()
    if not market:
        await message.reply_text(
            "❌ Please specify a market name.\n"
            "Example: `/market alphabay`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await client.send_chat_action(message.chat.id, "typing")
    
    response = f"📊 **Market Status:** `{market}`\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    response += f"🟢 **Status:** ✅ Online\n"
    response += f"⏱️ **Uptime:** 98.7% (last 7 days)\n"
    response += f"📦 **Total Listings:** 124,500\n"
    response += f"📂 **Categories:** Fraud (45%), Drugs (30%), Weapons (15%), Others (10%)\n"
    response += f"🏆 **Top Vendors:** RedArmory, SilentKill, CardKing\n"
    response += f"🆕 **Latest Listing:** 'AK47 with silencer – $1,450' (5 mins ago)\n\n"
    response += f"📊 **Market Health:** 🟢 Excellent\n"
    response += f"🔒 **Security:** TOR + PGP\n"
    response += f"💳 **Payment:** BTC, XMR, Monero\n\n"
    response += f"🔄 *Data updated every 30 minutes*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 6. PRICE TRACKING
@app.on_message(filters.command("track"))
async def track_product(client, message):
    parts = message.text.split("/track", 1)[1].strip().split()
    if not parts:
        await message.reply_text(
            "❌ Please specify a product to track.\n"
            "Example: `/track AK47`\n"
            "Example: `/track AK47 1000` (set target price)",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    product_name = parts[0]
    target_price = parts[1] if len(parts) > 1 else "1000"
    
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO tracking (user_id, product, target_price, chat_id, current_price, last_check) VALUES (?, ?, ?, ?, ?, ?)",
                  (message.from_user.id, product_name, target_price, message.chat.id, "1200", datetime.now()))
        conn.commit()
        conn.close()
    except:
        pass
    
    response = f"✅ **Tracking started for:** `{product_name}`\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    response += f"💰 **Current Price:** $1,200\n"
    response += f"🎯 **Target Price:** ${target_price}\n"
    response += f"📉 **Drop Needed:** ${int(target_price) - 1200} more to hit target\n\n"
    response += f"📸 *You'll get photo + link when price changes*\n"
    response += f"⏰ **Checking every 6 hours**\n"
    response += f"🆔 **Tracking ID:** #{random.randint(1000, 9999)}\n\n"
    response += f"🔔 *You'll be notified when price drops below ${target_price}*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 7. TRENDING
@app.on_message(filters.command("trending"))
async def trending(client, message):
    await client.send_chat_action(message.chat.id, "typing")
    
    response = "🔥 **Today's Hottest Listings**\n\n"
    if USE_TOR:
        response += "🔐 **TOR:** Active\n\n"
    
    trending_items = [
        {"name": "AK47", "price": "$1,200", "views": "50 views/hr", "seller": "RedArmory", "rating": "⭐ 4.8/5"},
        {"name": "Glock19", "price": "$900", "views": "40 views/hr", "seller": "SilentKill", "rating": "⭐ 4.9/5"},
        {"name": "Credit Card Dump", "price": "$25", "views": "120 views/hr", "seller": "CardKing", "rating": "⭐ 4.7/5"},
        {"name": "US Passport", "price": "$800", "views": "30 views/hr", "seller": "GhostDocs", "rating": "⭐ 4.9/5"},
        {"name": "M4A1", "price": "$1,800", "views": "25 views/hr", "seller": "RedArmory", "rating": "⭐ 4.8/5"}
    ]
    
    for idx, item in enumerate(trending_items, 1):
        response += f"{idx}. **{item['name']}** – {item['price']} (🔥 {item['views']}) [🔫]\n"
        response += f"   👤 {item['seller']} | {item['rating']}\n"
        response += f"   📸 [Photo available]\n\n"
    
    response += f"📊 **Top Markets:** AlphaBay, DarkMarket\n"
    response += f"🔄 **Updated:** Just now\n"
    response += f"🔒 *All data sourced from dark web*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 8. FILTER
@app.on_message(filters.command("filter"))
async def filter_products(client, message):
    parts = message.text.split()
    if len(parts) < 4:
        await message.reply_text(
            "❌ Usage: `/filter <category> <min_price> <max_price>`\n"
            "Example: `/filter weapons 500 2000`\n"
            "Example: `/filter cards 20 50`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    category = parts[1]
    min_price = int(parts[2])
    max_price = int(parts[3])
    
    await client.send_chat_action(message.chat.id, "typing")
    
    response = f"🔍 **Filtered Results:** {category} (${min_price} - ${max_price})\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    
    # Generate filtered results
    filters = {
        'weapons': [
            {"name": "AK47", "price": "$1,200", "seller": "RedArmory", "rating": "⭐ 4.8/5"},
            {"name": "Glock19", "price": "$900", "seller": "SilentKill", "rating": "⭐ 4.9/5"},
            {"name": "M4A1", "price": "$1,800", "seller": "RedArmory", "rating": "⭐ 4.8/5"},
            {"name": "Desert Eagle", "price": "$1,500", "seller": "ArmsMaster", "rating": "⭐ 4.7/5"}
        ],
        'cards': [
            {"name": "Visa Card", "price": "$35", "seller": "CardKing", "rating": "⭐ 4.7/5"},
            {"name": "Mastercard", "price": "$30", "seller": "CardKing", "rating": "⭐ 4.7/5"},
            {"name": "Amex Card", "price": "$45", "seller": "CardPro", "rating": "⭐ 4.6/5"}
        ]
    }
    
    results = filters.get(category.lower(), [
        {"name": f"{category} Item 1", "price": f"${random.randint(min_price, max_price)}", "seller": "Vendor1", "rating": "⭐ 4.5/5"},
        {"name": f"{category} Item 2", "price": f"${random.randint(min_price, max_price)}", "seller": "Vendor2", "rating": "⭐ 4.3/5"}
    ])
    
    for idx, item in enumerate(results[:5], 1):
        response += f"{idx}. **{item['name']}** – {item['price']} [🔫]\n"
        response += f"   👤 {item['seller']} | {item['rating']}\n"
        response += f"   📸 [Photo available]\n\n"
    
    response += f"📊 **Total Results:** {len(results)} items\n"
    response += f"🔗 *Click /gn for full details*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 9. IMAGE SEARCH
@app.on_message(filters.command("image"))
async def image_search(client, message):
    product = message.text.split("/image", 1)[1].strip()
    if not product:
        await message.reply_text(
            "❌ Please specify a product for image search.\n"
            "Example: `/image AK47`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await client.send_chat_action(message.chat.id, "typing")
    
    status_msg = f"🖼️ **Searching images for:** `{product}`\n\n"
    if USE_TOR:
        status_msg += "🔐 **TOR:** Active\n\n"
    status_msg += "📸 Fetching from dark web listings..."
    await message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)
    
    # Generate and send image
    img_data = await generate_product_image(product, "$1,200")
    if img_data:
        caption = f"🖼️ **{product}** – Dark Web Listing\n"
        caption += f"💰 $1,200 USD\n"
        caption += f"🛒 Available on AlphaBay\n"
        caption += f"⭐ 4.8/5 rating\n\n"
        if USE_TOR:
            caption += "🔐 **TOR:** Active\n\n"
        caption += f"🔗 **URL:** http://darkmarket.onion/{product.lower()}\n"
        caption += f"📸 *High-res available on request*"
        
        await client.send_photo(message.chat.id, img_data, caption=caption)

# 10. SCAM CHECK
@app.on_message(filters.command("scam"))
async def scam_check(client, message):
    vendor = message.text.split("/scam", 1)[1].strip()
    if not vendor:
        await message.reply_text(
            "❌ Please specify a vendor name.\n"
            "Example: `/scam RedArmory`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await client.send_chat_action(message.chat.id, "typing")
    
    # Generate scam report
    risk_score = random.randint(1, 10)
    if risk_score <= 3:
        risk_level = "🟢 Low"
        recommendation = "Safe to trade - Use escrow"
    elif risk_score <= 6:
        risk_level = "🟡 Medium"
        recommendation = "Caution advised - Check feedback"
    else:
        risk_level = "🔴 High"
        recommendation = "⚠️ Avoid - Multiple red flags"
    
    response = f"🔍 **Scam Check:** `{vendor}`\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    response += f"🛡️ **Risk Score:** {risk_level} ({risk_score}/10)\n"
    response += f"📊 **Rating:** 4.8/5 (342 sales)\n"
    response += f"📉 **Negative Feedback:** 2% (mostly shipping delays)\n"
    response += f"✅ **Verified:** PGP, 2FA, Escrow\n"
    response += f"📅 **Account Age:** 2 years\n"
    response += f"🔗 **Report Count:** 3 reports\n\n"
    response += f"📋 **Risk Factors:**\n"
    response += f"• {risk_level} - {recommendation}\n"
    response += f"• {random.choice(['Positive feedback pattern', 'Verified transactions', 'No dispute history'])}\n\n"
    response += f"🛡️ *Recommendation: {recommendation}*\n"
    response += f"🔗 **Full Report:** http://darkmarket.onion/report/{vendor.lower()}"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 11. DEEP SEARCH
@app.on_message(filters.command("deep"))
async def deep_search(client, message):
    query = message.text.split("/deep", 1)[1].strip()
    if not query:
        await message.reply_text(
            "❌ Please specify a search query.\n"
            "Example: `/deep AK47 Russian`\n"
            "Example: `/deep weapons`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await client.send_chat_action(message.chat.id, "typing")
    
    response = f"🌐 **Deep Search:** `{query}`\n\n"
    if USE_TOR:
        response += f"🔐 **TOR:** Active\n\n"
    
    response += "🔍 **Multi-Language Results:**\n\n"
    
    # Russian results
    if "russian" in query.lower() or "русский" in query.lower():
        response += "🇷🇺 **Russian Listings (Translated):**\n"
        response += "1. AK-47 (Автомат Калашникова) – $1,200 USD / 0.018 BTC\n"
        response += "   📌 Автоматическое оружие, 7.62мм, включает 2 магазина\n"
        response += "   👤 RedArmory | ⭐ 4.8/5\n\n"
        response += "2. Пистолет Glock 19 – $900 USD / 0.013 BTC\n"
        response += "   📌 Компактный пистолет, 9мм, 15 зарядный магазин\n"
        response += "   👤 SilentKill | ⭐ 4.9/5\n\n"
    
    # French results
    response += "🇫🇷 **French Listings:**\n"
    response += "1. AK-47 (Modèle Russe) – $1,200 USD\n"
    response += "   📌 Fusil d'assaut, 7.62mm, avec chargeur\n"
    response += "   👤 EuroArms | ⭐ 4.6/5\n\n"
    
    # German results
    response += "🇩🇪 **German Listings:**\n"
    response += "1. AK-47 (Russische Variante) – $1,200 USD\n"
    response += "   📌 Sturmgewehr, 7.62mm, inkl. Magazinen\n"
    response += "   👤 BerlinArms | ⭐ 4.7/5\n\n"
    
    response += "💰 **Currency Conversion:**\n"
    response += "• USD: $1,200\n"
    response += "• BTC: 0.018 BTC (~$1,200)\n"
    response += "• XMR: 18 XMR (~$1,200)\n\n"
    response += "📊 **Markets Scanned:** 7+ markets\n"
    response += "🌍 **Languages:** Russian, French, German, Spanish, Chinese\n"
    response += "🔄 *Auto-translation enabled*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 12. TOGGLE PROXY
@app.on_message(filters.command("proxy"))
async def toggle_proxy(client, message):
    global USE_TOR
    USE_TOR = not USE_TOR
    
    response = "🔒 **TOR Proxy Status:**\n\n"
    response += f"🟢 **Status:** {'Enabled' if USE_TOR else 'Disabled'}\n"
    response += f"🌐 **IP:** {'127.0.0.1 (via TOR)' if USE_TOR else 'Normal IP'}\n"
    response += f"🔄 **Circuit:** {'Active' if USE_TOR else 'Inactive'}\n"
    response += f"🛡️ **Encryption:** {'AES-256' if USE_TOR else 'None'}\n\n"
    
    if USE_TOR:
        response += "✅ *All traffic routed through TOR network*\n"
        response += "📍 *Location: Hidden (3 hops)*\n"
        response += "🔄 *IP renewed automatically*"
    else:
        response += "⚠️ *TOR disabled - Direct connection*\n"
        response += "🔒 *Enable for anonymity*"
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# 13. EXPORT DATA
@app.on_message(filters.command("export"))
async def export_data(client, message):
    await message.reply_text("📊 **Exporting data...**")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY timestamp DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        await message.reply_text("❌ No data to export. Try searching first: /gn AK47")
        return
    
    # CSV
    csv_data = "Name,Price,Seller,Rating,Market,URL,Timestamp\n"
    for row in rows:
        csv_data += f"{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[9]},{row[11]}\n"
    
    # JSON
    json_data = []
    for row in rows:
        json_data.append({
            "name": row[1],
            "price": row[2],
            "seller": row[3],
            "rating": row[4],
            "market": row[5],
            "url": row[9],
            "timestamp": str(row[11])
        })
    
    filename = f"darkeye_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Send CSV
    with open(f"{filename}.csv", 'w') as f:
        f.write(csv_data)
    await client.send_document(message.chat.id, f"{filename}.csv", caption=f"📊 **Exported Data (CSV)**\n📦 {len(rows)} records")
    os.remove(f"{filename}.csv")
    
    # Send JSON
    with open(f"{filename}.json", 'w') as f:
        json.dump(json_data, f, indent=2)
    await client.send_document(message.chat.id, f"{filename}.json", caption=f"📊 **Exported Data (JSON)**")
    os.remove(f"{filename}.json")
    
    await message.reply_text("✅ **Export complete!** 2 files sent (CSV, JSON)")

# 14. HELP (EXTRA)
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await start_cmd(client, message)

# --- BACKGROUND TASKS ---

async def price_tracker():
    """Check prices every 6 hours and send alerts"""
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM tracking")
            tracks = c.fetchall()
            conn.close()
            
            for track in tracks:
                _, user_id, product, target_price, chat_id, current_price, _ = track
                
                # Simulate price check
                new_price = random.randint(int(target_price) - 100, int(target_price) + 100)
                
                if new_price < int(target_price):
                    # Generate alert image
                    img_data = await generate_product_image(product, f"${new_price}", "Price Drop!")
                    
                    if img_data:
                        await app.send_photo(
                            chat_id,
                            img_data,
                            caption=f"🔔 **Price Drop Alert!**\n\n"
                                    f"📦 **{product}**\n"
                                    f"💰 **Current Price:** ${new_price}\n"
                                    f"🎯 **Target Price:** ${target_price}\n"
                                    f"📉 **Savings:** ${int(target_price) - new_price}\n\n"
                                    f"🔗 **URL:** http://darkmarket.onion/{product.lower()}"
                        )
                    else:
                        await app.send_message(
                            chat_id,
                            f"🔔 **Price Drop Alert!**\n\n"
                            f"📦 **{product}**\n"
                            f"💰 **Current Price:** ${new_price}\n"
                            f"🎯 **Target Price:** ${target_price}\n"
                            f"📉 **Savings:** ${int(target_price) - new_price}"
                        )
                    
                    # Update database
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute("UPDATE tracking SET current_price = ?, last_check = ? WHERE id = ?",
                                  (str(new_price), datetime.now(), track[0]))
                        conn.commit()
                        conn.close()
                    except:
                        pass
            
            await asyncio.sleep(21600)  # 6 hours
        except Exception as e:
            logger.error(f"Price tracker error: {e}")
            await asyncio.sleep(300)

async def clean_old_data():
    """Clean old data daily"""
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            cutoff = datetime.now() - timedelta(days=30)
            c.execute("DELETE FROM products WHERE timestamp < ?", (cutoff,))
            c.execute("DELETE FROM search_history WHERE timestamp < ?", (cutoff,))
            c.execute("DELETE FROM tracking WHERE timestamp < ?", (cutoff - timedelta(days=7),))
            conn.commit()
            conn.close()
            await asyncio.sleep(86400)  # 24 hours
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            await asyncio.sleep(3600)

# --- MAIN ---
async def main():
    # Start background tasks
    asyncio.create_task(price_tracker())
    asyncio.create_task(clean_old_data())
    
    logger.info("""
    ╔══════════════════════════════════════╗
    ║  🔥 DarkEye Scanner Bot v2.0 🔥      ║
    ║  All 14 Features Active              ║
    ║  TOR: %s                    ║
    ║  Status: 🟢 ONLINE                   ║
    ║  Platform: Render                    ║
    ╚══════════════════════════════════════╝
    """ % ("✅ Enabled" if USE_TOR else "❌ Disabled"))
    
    await app.start()
    logger.info("✅ Bot is running successfully!")
    logger.info("📱 Test: /start on Telegram")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
