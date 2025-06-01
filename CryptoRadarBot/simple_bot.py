#!/usr/bin/env python3
"""
Simple Telegram Crypto Bot
"""

import asyncio
import aiohttp
import logging
import requests
from config import BOT_TOKEN, COINGECKO_API_BASE

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCryptoBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        
    async def send_message(self, chat_id, text):
        """Send message to Telegram"""
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()
    
    def get_crypto_price(self, coin_id):
        """Get cryptocurrency price"""
        try:
            url = f"{COINGECKO_API_BASE}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd,try',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if coin_id in data:
                return data[coin_id]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None
    
    def get_top_gainers(self):
        """Get top gaining cryptocurrencies"""
        try:
            url = f"{COINGECKO_API_BASE}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 50,
                'page': 1,
                'price_change_percentage': '1h'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Sort by 1h change and get top 5
            sorted_coins = sorted(data, key=lambda x: x.get('price_change_percentage_1h_in_currency', 0), reverse=True)[:5]
            return sorted_coins
            
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return None
    
    async def handle_message(self, message):
        """Handle incoming messages"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip().lower()
        
        try:
            if text.startswith('/start'):
                welcome_text = """
🔍 **Kripto Radar Botu'na hoş geldin!** 🚀

Bu bot ile kripto para fiyatlarını takip edebilirsin:

📊 **Komutlar:**
• `/fiyat bitcoin` - Bitcoin fiyatını öğren
• `/btc` - Bitcoin fiyatı
• `/eth` - Ethereum fiyatı
• `/yukselenler` - En çok yükselen 5 coin
• `/help` - Yardım menüsü

💡 **İpucu:** Sadece kripto para ismini yazarak da fiyat öğrenebilirsin!
                """
                await self.send_message(chat_id, welcome_text)
                
            elif text.startswith('/help'):
                help_text = """
🆘 **Yardım Menüsü**

**Kullanılabilir Komutlar:**
🏠 `/start` - Botu yeniden başlat
📊 `/fiyat <coin>` - Kripto para fiyatını öğren
₿ `/btc` - Bitcoin fiyatı
⟠ `/eth` - Ethereum fiyatı
🚀 `/yukselenler` - En çok yükselen 5 coin

**Örnek Kullanım:**
• `bitcoin` veya `btc`
• `/fiyat ethereum`
                """
                await self.send_message(chat_id, help_text)
                
            elif text.startswith('/btc'):
                price_data = self.get_crypto_price('bitcoin')
                if price_data:
                    usd_price = price_data.get('usd', 0)
                    try_price = price_data.get('try', 0)
                    change_24h = price_data.get('usd_24h_change', 0)
                    
                    message_text = f"💰 **Bitcoin (BTC) Fiyat Bilgileri**\n\n"
                    message_text += f"💵 **Fiyat:** ${usd_price:,.2f}\n"
                    if try_price:
                        message_text += f"🇹🇷 **TL:** ₺{try_price:,.2f}\n"
                    message_text += f"📊 **24s Değişim:** %{change_24h:.2f}\n"
                    message_text += f"\n🕐 _Güncelleme: Şimdi_"
                    
                    await self.send_message(chat_id, message_text)
                else:
                    await self.send_message(chat_id, "❌ Bitcoin fiyatı alınamadı, lütfen daha sonra tekrar deneyin.")
                    
            elif text.startswith('/eth'):
                price_data = self.get_crypto_price('ethereum')
                if price_data:
                    usd_price = price_data.get('usd', 0)
                    try_price = price_data.get('try', 0)
                    change_24h = price_data.get('usd_24h_change', 0)
                    
                    message_text = f"💰 **Ethereum (ETH) Fiyat Bilgileri**\n\n"
                    message_text += f"💵 **Fiyat:** ${usd_price:,.2f}\n"
                    if try_price:
                        message_text += f"🇹🇷 **TL:** ₺{try_price:,.2f}\n"
                    message_text += f"📊 **24s Değişim:** %{change_24h:.2f}\n"
                    message_text += f"\n🕐 _Güncelleme: Şimdi_"
                    
                    await self.send_message(chat_id, message_text)
                else:
                    await self.send_message(chat_id, "❌ Ethereum fiyatı alınamadı, lütfen daha sonra tekrar deneyin.")
                    
            elif text.startswith('/yukselenler'):
                gainers = self.get_top_gainers()
                if gainers:
                    message_text = "🚀 **Son 1 Saatte En Çok Yükselen 5 Coin:**\n\n"
                    for i, coin in enumerate(gainers, 1):
                        symbol = coin['symbol'].upper()
                        change = coin.get('price_change_percentage_1h_in_currency', 0)
                        price = coin['current_price']
                        message_text += f"{i}. **{symbol}**: +%{change:.2f} | ${price:.4f}\n"
                    
                    message_text += f"\n🕐 _Güncelleme: Şimdi_"
                    await self.send_message(chat_id, message_text)
                else:
                    await self.send_message(chat_id, "❌ Yükselen coinler listesi alınamadı, lütfen daha sonra tekrar deneyin.")
                    
            elif text.startswith('/topgainers'):
                gainers = self.get_top_gainers()
                if gainers:
                    message_text = "🚀 **Top 5 Gaining Coins in Last Hour:**\n\n"
                    for i, coin in enumerate(gainers, 1):
                        symbol = coin['symbol'].upper()
                        change = coin.get('price_change_percentage_1h_in_currency', 0)
                        price = coin['current_price']
                        message_text += f"{i}. **{symbol}**: +{change:.2f}% | ${price:.4f}\n"
                    
                    message_text += f"\n🕐 _Updated: Now_"
                    await self.send_message(chat_id, message_text)
                else:
                    await self.send_message(chat_id, "❌ Could not fetch top gainers list, please try again later.")
                    
            elif text.startswith('/fiyat '):
                coin_name = text.replace('/fiyat ', '').strip()
                # Simple coin mapping
                coin_map = {
                    'bitcoin': 'bitcoin', 'btc': 'bitcoin',
                    'ethereum': 'ethereum', 'eth': 'ethereum',
                    'binance': 'binancecoin', 'bnb': 'binancecoin'
                }
                
                coin_id = coin_map.get(coin_name, coin_name)
                price_data = self.get_crypto_price(coin_id)
                
                if price_data:
                    usd_price = price_data.get('usd', 0)
                    try_price = price_data.get('try', 0)
                    change_24h = price_data.get('usd_24h_change', 0)
                    
                    message_text = f"💰 **{coin_name.upper()} Fiyat Bilgileri**\n\n"
                    message_text += f"💵 **Fiyat:** ${usd_price:,.2f}\n"
                    if try_price:
                        message_text += f"🇹🇷 **TL:** ₺{try_price:,.2f}\n"
                    message_text += f"📊 **24s Değişim:** %{change_24h:.2f}\n"
                    message_text += f"\n🕐 _Güncelleme: Şimdi_"
                    
                    await self.send_message(chat_id, message_text)
                else:
                    await self.send_message(chat_id, f"❌ '{coin_name}' bulunamadı. Desteklenen coinler: bitcoin, ethereum, binance")
                    
            else:
                # Check if it's a simple coin name
                coin_map = {
                    'bitcoin': 'bitcoin', 'btc': 'bitcoin',
                    'ethereum': 'ethereum', 'eth': 'ethereum'
                }
                
                if text in coin_map:
                    coin_id = coin_map[text]
                    price_data = self.get_crypto_price(coin_id)
                    
                    if price_data:
                        usd_price = price_data.get('usd', 0)
                        change_24h = price_data.get('usd_24h_change', 0)
                        
                        message_text = f"💰 **{text.upper()} Fiyat:** ${usd_price:,.2f}\n"
                        message_text += f"📊 **24s Değişim:** %{change_24h:.2f}"
                        
                        await self.send_message(chat_id, message_text)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_message(chat_id, "⚠️ Bir hata oluştu, lütfen daha sonra tekrar deneyin.")
    
    async def get_updates(self):
        """Get updates from Telegram"""
        url = f"{self.api_url}/getUpdates"
        params = {'offset': self.offset, 'timeout': 30}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get('ok'):
                        return data.get('result', [])
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    async def run(self):
        """Main bot loop"""
        logger.info("🚀 Kripto Radar Botu başlatılıyor...")
        
        while True:
            try:
                updates = await self.get_updates()
                
                for update in updates:
                    self.offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        await self.handle_message(update['message'])
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

def main():
    bot = SimpleCryptoBot(BOT_TOKEN)
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()