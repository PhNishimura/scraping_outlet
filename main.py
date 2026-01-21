import requests
from bs4 import BeautifulSoup
import re
import telegram
import asyncio
import os
import time
import schedule
import json

# Get absolute path of the directory where the script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# YOUR BOT_TOKEN AND CHAT_ID
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

# BERZERK URLS
BASE_URL = 'https://berzerk.com.br'
PAGE_URL = f'{BASE_URL}/collections/outlet'

MEMORY_JSON_FILE = os.path.join(CURRENT_DIR, 'monitored_products.json')

# --- HELPER FUNCTIONS ---

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2."""
    reserved_chars = r'([_*\[\]()~`>#+\-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

def load_saved_data() -> dict:
    """Loads previously monitored products from the JSON file."""
    if not os.path.exists(MEMORY_JSON_FILE):
        return {}
    try:
        with open(MEMORY_JSON_FILE, 'r', encoding='utf-8') as f:
            product_list = json.load(f)
            # Convert list back to dictionary keyed by link
            return {prod['link']: prod for prod in product_list}
    except (json.JSONDecodeError, IOError):
        return {}

def save_product_data(product_data: dict):
    """Saves the latest state of products to the JSON file."""
    with open(MEMORY_JSON_FILE, 'w', encoding='utf-8') as f:
        list_to_save = list(product_data.values())
        json.dump(list_to_save, f, indent=4, ensure_ascii=False)

async def send_telegram_message(bot_token, chat_id, message):
    """Sends a message to your Telegram chat or channel."""
    try:
        bot = telegram.Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')
        print(f"✅ Notification sent successfully to Telegram!")
    except Exception as e:
        print(f"❌ Failed to send message to Telegram: {e}")

# --- MAIN FUNCTION ---

async def monitor_berzerk():
    print("🤖 Starting silent monitoring on Berzerk...")
    
    saved_data = load_saved_data()
    print(f"📄 Found {len(saved_data)} products in JSON memory.")

    try:
        page = requests.get(PAGE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')

        current_products_on_page = {}

        # Updated selector to find the new product info container.
        # The 'card-information' class groups name, price, and link.
        info_blocks = soup.find_all('div', class_="card-information")
        
        if not info_blocks:
            print("⚠️ No product blocks found on the page. Aborting check to protect memory.")
            return

        print(f"🔎 Found {len(info_blocks)} products on the page. Verifying...")

        # --- Loop 1: Detect NEW products and PRICE changes ---
        for info_div in info_blocks:
            # Robust link search: looking for 'a' tag with href containing '/products/'
            link_tag = info_div.find('a', href=re.compile(r'/products/'))
            if not link_tag:
                continue
            
            full_link = BASE_URL + link_tag['href']
            
            # Product name is now inside an <a> tag with class 'card-title'
            name_tag = info_div.find('a', class_="card-title")
            name = name_tag.text.strip() if name_tag else "Name not found"
            
            # Price structure changed. Logic:
            # 1. Look for sale price ('price-item--sale')
            # 2. If not found, look for regular price ('price-item--regular')
            price_tag = info_div.find('span', class_='price-item--sale')
            if not price_tag:
                regular_price_container = info_div.find('div', class_='price__regular')
                if regular_price_container:
                    price_tag = regular_price_container.find('span', class_='price-item--regular')

            current_price_text = "Price not found"
            if price_tag:
                current_price_text = price_tag.text.strip()

            current_product_info = {'link': full_link, 'name': name, 'price': current_price_text}
            current_products_on_page[full_link] = current_product_info

            # Scenario 1: The product is NEW
            if full_link not in saved_data:
                print(f"🎉 NEW PRODUCT FOUND: {name}")
                message = (
                    f"🚨 *NEW DROP AT BERZERK* 🚨\n\n"
                    f"👕 *Product*: {escape_markdown_v2(name)}\n"
                    f"💰 *Price*: {escape_markdown_v2(current_price_text)}\n\n"
                    f"🔗 *Check it out*:\n"
                    f"[{escape_markdown_v2('Click here to view')}]({full_link})"
                )
                await send_telegram_message(BOT_TOKEN, CHAT_ID, message)
            
            # Scenario 2: The product EXISTS, check for PRICE CHANGE
            else:
                saved_price = saved_data[full_link].get('price', 'Price not saved')
                if current_price_text != saved_price and current_price_text != "Price not found":
                    print(f"💰 PRICE CHANGE: {name}")
                    message = (
                        f"💸 *PRICE CHANGE DETECTED* 💸\n\n"
                        f"👕 *Product*: {escape_markdown_v2(name)}\n"
                        f"📉 *Old Price*: {escape_markdown_v2(saved_price)}\n"
                        f"📈 *New Price*: {escape_markdown_v2(current_price_text)}\n\n"
                        f"🔗 *Check it out*:\n"
                        f"[{escape_markdown_v2('Click here to view')}]({full_link})"
                    )
                    await send_telegram_message(BOT_TOKEN, CHAT_ID, message)
            
            await asyncio.sleep(1) # Short pause to be polite to the server

        # --- Loop 2: Detect REMOVED products ---
        saved_links_set = set(saved_data.keys())
        current_links_set = set(current_products_on_page.keys())
        
        removed_links = saved_links_set - current_links_set

        if removed_links:
            print(f"🗑️ Found {len(removed_links)} removed/sold-out products.")
            for removed_link in removed_links:
                removed_product = saved_data[removed_link]
                removed_name = removed_product.get('name', 'Name not available')
                
                message = (
                    f"❌ *PRODUCT REMOVED OR SOLD OUT* ❌\n\n"
                    f"👕 *Product*: {escape_markdown_v2(removed_name)}\n\n"
                    f"This item is no longer listed on the outlet page\\."
                )
                await send_telegram_message(BOT_TOKEN, CHAT_ID, message)
                await asyncio.sleep(1)

        # Save the latest state of all products FOUND ON THE PAGE
        save_product_data(current_products_on_page)
        print(f"💾 Data for {len(current_products_on_page)} products saved to JSON.")
        
        print("🏁 Monitoring finished.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error accessing the page: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        print("❗️ JSON file was not modified due to error.")

# --- ENTRY POINT AND SCHEDULING ---

def run_task():
    print("\n----------------------------------------------------")
    print(f"[{time.ctime()}] Triggering scheduled check...")
    try:
        asyncio.run(monitor_berzerk())
    except Exception as e:
        print(f"❌ Error executing async task: {e}")
    print("----------------------------------------------------\n")

if __name__ == "__main__":
    if "YOUR_BOT_TOKEN" in BOT_TOKEN or "YOUR_CHAT_ID" in CHAT_ID:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ATTENTION: FILL IN YOUR BOT_TOKEN AND CHAT_ID !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        # Configure schedule to run every 2 to 5 minutes
        schedule.every(2).to(5).minutes.do(run_task)

        print("✅ Schedule configured! Script will run at intervals of 2 to 5 minutes.")
        print("🚀 Running first check immediately...")
        
        run_task()

        while True:
            schedule.run_pending()
            time.sleep(1)