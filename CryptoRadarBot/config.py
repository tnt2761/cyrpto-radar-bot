"""
Konfigürasyon dosyası
Configuration file for the Telegram bot
"""

import os

# Telegram Bot Token - Gizli bilgilerden alınır
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required!")

# CoinGecko API ayarları
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
API_TIMEOUT = 10  # saniye

# Bot ayarları
MAX_RETRIES = 3
CACHE_DURATION = 60  # saniye

# Desteklenen kripto paralar (Türkçe isimler ile)
CRYPTO_ALIASES = {
    'btc': 'bitcoin',
    'bitcoin': 'bitcoin',
    'eth': 'ethereum',
    'ethereum': 'ethereum',
    'bnb': 'binancecoin',
    'binance': 'binancecoin',
    'xrp': 'ripple',
    'ripple': 'ripple',
    'ada': 'cardano',
    'cardano': 'cardano',
    'sol': 'solana',
    'solana': 'solana',
    'doge': 'dogecoin',
    'dogecoin': 'dogecoin',
    'dot': 'polkadot',
    'polkadot': 'polkadot',
    'avax': 'avalanche-2',
    'avalanche': 'avalanche-2',
    'ltc': 'litecoin',
    'litecoin': 'litecoin'
}

# Mesaj şablonları
MESSAGES = {
    'welcome': """
🔍 **Kripto Radar Botu'na hoş geldin!** 🚀

Bu bot ile kripto para fiyatlarını takip edebilirsin:

📊 **Komutlar:**
• `/fiyat <coin>` - Belirli bir kripto paranın fiyatını öğren
• `/btc` - Bitcoin fiyatı
• `/eth` - Ethereum fiyatı
• `/top10` - En popüler 10 kripto para
• `/ara <isim>` - Kripto para ara
• `/help` - Yardım menüsü

**Örnek:** `/fiyat bitcoin` veya `/fiyat btc`

💡 **İpucu:** Sadece kripto para ismini yazarak da fiyat öğrenebilirsin!
""",
    
    'help': """
🆘 **Yardım Menüsü**

**Kullanılabilir Komutlar:**

🏠 `/start` - Botu yeniden başlat
📊 `/fiyat <coin>` - Kripto para fiyatını öğren
₿ `/btc` - Bitcoin fiyatı ve bilgileri  
⟠ `/eth` - Ethereum fiyatı ve bilgileri
🔟 `/top10` - Top 10 kripto para listesi
🔍 `/ara <isim>` - Kripto para ara

**Desteklenen Kripto Paralar:**
Bitcoin (BTC), Ethereum (ETH), Binance Coin (BNB), 
XRP, Cardano (ADA), Solana (SOL), Dogecoin (DOGE),
Polkadot (DOT), Avalanche (AVAX), Litecoin (LTC)

**Örnek Kullanım:**
• `bitcoin` veya `btc`
• `/fiyat ethereum`
• `/ara cardano`

❓ Sorularınız için: @LeventKriptoBot
""",
    
    'error_api': "⚠️ Şu anda kripto para verilerine ulaşılamıyor. Lütfen daha sonra tekrar deneyin.",
    'error_not_found': "❌ Bu kripto para bulunamadı. Lütfen geçerli bir kripto para ismi girin.",
    'error_invalid': "❌ Geçersiz komut. /help komutunu kullanarak yardım alabilirsiniz.",
    'processing': "⏳ Veriler getiriliyor, lütfen bekleyin..."
}
