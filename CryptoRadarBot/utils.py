"""
Yardımcı fonksiyonlar
Utility functions for formatting and data processing
"""

import re
from typing import Dict, Optional
from config import CRYPTO_ALIASES

def format_price(price: float, currency: str = "USD") -> str:
    """Fiyatı formatlar"""
    if currency.upper() == "TRY":
        if price >= 1:
            return f"₺{price:,.2f}"
        else:
            return f"₺{price:.6f}"
    else:
        if price >= 1:
            return f"${price:,.2f}"
        else:
            return f"${price:.6f}"

def format_percentage(percentage: float) -> str:
    """Yüzdelik değişimi formatlar"""
    if percentage > 0:
        return f"📈 +%{percentage:.2f}"
    elif percentage < 0:
        return f"📉 %{percentage:.2f}"
    else:
        return f"➡️ %{percentage:.2f}"

def format_market_cap(market_cap: float) -> str:
    """Piyasa değerini formatlar"""
    if market_cap >= 1_000_000_000_000:  # Trillion
        return f"${market_cap/1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:  # Billion
        return f"${market_cap/1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:  # Million
        return f"${market_cap/1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def format_volume(volume: float) -> str:
    """İşlem hacmini formatlar"""
    return format_market_cap(volume)

def get_coin_id(user_input: str) -> Optional[str]:
    """Kullanıcı girdisinden coin ID'si çıkarır"""
    user_input = user_input.lower().strip()
    
    # Direkt alias kontrolü
    if user_input in CRYPTO_ALIASES:
        return CRYPTO_ALIASES[user_input]
    
    # Kısmi eşleşme kontrolü
    for alias, coin_id in CRYPTO_ALIASES.items():
        if user_input in alias or alias in user_input:
            return coin_id
    
    # Eğer bulunamazsa, orijinal girdiyi döndür
    return user_input

def create_price_message(coin_data: Dict, coin_name: str) -> str:
    """Fiyat mesajı oluşturur"""
    try:
        usd_price = coin_data.get('usd', 0)
        try_price = coin_data.get('try', 0)
        change_24h = coin_data.get('usd_24h_change', 0)
        market_cap = coin_data.get('usd_market_cap', 0)
        volume_24h = coin_data.get('usd_24h_vol', 0)
        
        message = f"💰 **{coin_name.upper()} Fiyat Bilgileri**\n\n"
        message += f"💵 **Fiyat:** {format_price(usd_price, 'USD')}\n"
        
        if try_price:
            message += f"🇹🇷 **TL:** {format_price(try_price, 'TRY')}\n"
        
        message += f"📊 **24s Değişim:** {format_percentage(change_24h)}\n"
        
        if market_cap:
            message += f"🏪 **Piyasa Değeri:** {format_market_cap(market_cap)}\n"
        
        if volume_24h:
            message += f"📈 **24s Hacim:** {format_volume(volume_24h)}\n"
        
        message += f"\n🕐 _Güncelleme: Şimdi_"
        
        return message
        
    except Exception as e:
        return f"❌ Fiyat bilgileri formatlanırken hata oluştu: {str(e)}"

def create_top_coins_message(coins_data: list) -> str:
    """Top 10 kripto para mesajı oluşturur"""
    try:
        message = "🏆 **Top 10 Kripto Para**\n\n"
        
        for i, coin in enumerate(coins_data, 1):
            name = coin.get('name', 'Bilinmeyen')
            symbol = coin.get('symbol', '').upper()
            price = coin.get('current_price', 0)
            change_24h = coin.get('price_change_percentage_24h', 0)
            
            change_emoji = "📈" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
            
            message += f"{i}. **{name} ({symbol})**\n"
            message += f"   💰 {format_price(price, 'USD')} "
            message += f"{change_emoji} %{change_24h:.2f}\n\n"
        
        message += "🕐 _Güncelleme: Şimdi_"
        return message
        
    except Exception as e:
        return f"❌ Top 10 listesi formatlanırken hata oluştu: {str(e)}"

def clean_user_input(text: str) -> str:
    """Kullanıcı girdisini temizler"""
    # Sadece harf, rakam ve bazı özel karakterleri bırak
    cleaned = re.sub(r'[^\w\s-.]', '', text)
    return cleaned.strip().lower()

def is_valid_crypto_query(text: str) -> bool:
    """Geçerli kripto para sorgusu mu kontrol eder"""
    cleaned = clean_user_input(text)
    
    # En az 2 karakter olmalı
    if len(cleaned) < 2:
        return False
    
    # Bilinen alias'lardan biri mi?
    if cleaned in CRYPTO_ALIASES:
        return True
    
    # Kripto para ismi benzeri mi? (harf ve rakam içermeli)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9\-]*$', cleaned):
        return True
    
    return False
