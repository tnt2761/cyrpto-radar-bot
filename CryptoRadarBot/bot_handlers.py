"""
Telegram bot komut işleyicileri
Telegram bot command handlers
"""

import logging
import requests
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from crypto_api import get_crypto_api
from utils import (
    get_coin_id, 
    create_price_message, 
    create_top_coins_message,
    clean_user_input,
    is_valid_crypto_query
)
from config import MESSAGES

logger = logging.getLogger(__name__)

class BotHandlers:
    """Telegram bot komut işleyicilerini içeren sınıf"""
    
    def __init__(self):
        self.processing_users = set()  # İşlem yapılan kullanıcıları takip et
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /start komutu - Hoş geldin mesajı gönderir
        """
        try:
            await update.message.reply_text(
                MESSAGES['welcome'],
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Start command used by user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(MESSAGES['error_api'])
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /help komutu - Yardım mesajı gönderir
        """
        try:
            await update.message.reply_text(
                MESSAGES['help'],
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Help command used by user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text(MESSAGES['error_api'])
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /fiyat <coin> komutu - Belirli kripto para fiyatını gösterir
        """
        user_id = update.effective_user.id
        
        if user_id in self.processing_users:
            await update.message.reply_text("⏳ Zaten bir işlem devam ediyor, lütfen bekleyin...")
            return
        
        try:
            self.processing_users.add(user_id)
            
            # Parametreleri kontrol et
            if not context.args:
                await update.message.reply_text(
                    "❓ Hangi kripto paranın fiyatını öğrenmek istiyorsunuz?\n"
                    "**Örnek:** `/fiyat bitcoin` veya `/fiyat btc`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            coin_query = ' '.join(context.args).lower()
            coin_id = get_coin_id(coin_query)
            
            # İşlem mesajı gönder
            processing_msg = await update.message.reply_text(MESSAGES['processing'])
            
            async with await get_crypto_api() as api:
                coin_data = await api.get_coin_price(coin_id)
                
                if coin_data:
                    message = create_price_message(coin_data, coin_query)
                    await processing_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
                    logger.info(f"Price command successful for {coin_query} by user {user_id}")
                else:
                    await processing_msg.edit_text(MESSAGES['error_not_found'])
                    logger.warning(f"Coin not found: {coin_query} by user {user_id}")
        
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            try:
                await processing_msg.edit_text(MESSAGES['error_api'])
            except:
                await update.message.reply_text(MESSAGES['error_api'])
        
        finally:
            self.processing_users.discard(user_id)
    
    async def btc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /btc komutu - Bitcoin fiyatını gösterir
        """
        context.args = ['bitcoin']
        await self.price_command(update, context)
    
    async def eth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /eth komutu - Ethereum fiyatını gösterir
        """
        context.args = ['ethereum']
        await self.price_command(update, context)
    
    async def top10_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /top10 komutu - En popüler 10 kripto parayı listeler
        """
        user_id = update.effective_user.id
        
        if user_id in self.processing_users:
            await update.message.reply_text("⏳ Zaten bir işlem devam ediyor, lütfen bekleyin...")
            return
        
        try:
            self.processing_users.add(user_id)
            
            # İşlem mesajı gönder
            processing_msg = await update.message.reply_text(MESSAGES['processing'])
            
            async with await get_crypto_api() as api:
                coins_data = await api.get_top_cryptocurrencies(10)
                
                if coins_data:
                    message = create_top_coins_message(coins_data)
                    await processing_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
                    logger.info(f"Top10 command successful by user {user_id}")
                else:
                    await processing_msg.edit_text(MESSAGES['error_api'])
                    
        except Exception as e:
            logger.error(f"Error in top10 command: {e}")
            try:
                await processing_msg.edit_text(MESSAGES['error_api'])
            except:
                await update.message.reply_text(MESSAGES['error_api'])
        
        finally:
            self.processing_users.discard(user_id)
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /ara <isim> komutu - Kripto para arar
        """
        user_id = update.effective_user.id
        
        if user_id in self.processing_users:
            await update.message.reply_text("⏳ Zaten bir işlem devam ediyor, lütfen bekleyin...")
            return
        
        try:
            self.processing_users.add(user_id)
            
            if not context.args:
                await update.message.reply_text(
                    "❓ Hangi kripto parayı aramak istiyorsunuz?\n"
                    "**Örnek:** `/ara cardano`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            search_query = ' '.join(context.args)
            
            # İşlem mesajı gönder
            processing_msg = await update.message.reply_text(MESSAGES['processing'])
            
            async with await get_crypto_api() as api:
                search_results = await api.search_cryptocurrency(search_query)
                
                if search_results:
                    message = "🔍 **Arama Sonuçları:**\n\n"
                    
                    for coin in search_results:
                        name = coin.get('name', 'Bilinmeyen')
                        symbol = coin.get('symbol', '').upper()
                        message += f"• **{name} ({symbol})**\n"
                    
                    message += f"\n💡 Fiyat öğrenmek için: `/fiyat <coin ismi>`"
                    
                    await processing_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
                    logger.info(f"Search command successful for '{search_query}' by user {user_id}")
                else:
                    await processing_msg.edit_text(
                        f"❌ '{search_query}' için sonuç bulunamadı.\n"
                        "Farklı bir arama terimi deneyin."
                    )
                    
        except Exception as e:
            logger.error(f"Error in search command: {e}")
            try:
                await processing_msg.edit_text(MESSAGES['error_api'])
            except:
                await update.message.reply_text(MESSAGES['error_api'])
        
        finally:
            self.processing_users.discard(user_id)
    
    async def top_gainers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        /yukselenler komutu - Son 1 saatte en çok yükselen 5 kripto parayı gösterir
        """
        user_id = update.effective_user.id
        
        if user_id in self.processing_users:
            await update.message.reply_text("⏳ Zaten bir işlem devam ediyor, lütfen bekleyin...")
            return
        
        try:
            self.processing_users.add(user_id)
            
            # İşlem mesajı gönder
            processing_msg = await update.message.reply_text(MESSAGES['processing'])
            
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 50,
                'page': 1,
                'price_change_percentage': '1h'
            }

            response = requests.get(url, params=params)
            data = response.json()

            # En çok yükselen 5 coini sırala
            sorted_coins = sorted(data, key=lambda x: x.get('price_change_percentage_1h_in_currency', 0), reverse=True)[:5]

            message = "🚀 **Son 1 Saatte En Çok Yükselen 5 Coin:**\n\n"
            for i, coin in enumerate(sorted_coins, 1):
                isim = coin['symbol'].upper()
                degisim = round(coin.get('price_change_percentage_1h_in_currency', 0), 2)
                fiyat = round(coin['current_price'], 4)
                message += f"{i}. **{isim}**: +%{degisim} | ${fiyat}\n"
            
            message += f"\n🕐 _Güncelleme: Şimdi_"
            
            await processing_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
            logger.info(f"Top gainers command successful by user {user_id}")
                    
        except Exception as e:
            logger.error(f"Error in top gainers command: {e}")
            try:
                await processing_msg.edit_text(MESSAGES['error_api'])
            except:
                await update.message.reply_text(MESSAGES['error_api'])
        
        finally:
            self.processing_users.discard(user_id)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Metin mesajlarını işler - Kripto para ismi algılarsa fiyat gösterir
        """
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id in self.processing_users:
            return
        
        try:
            # Kullanıcı girdisini temizle
            cleaned_text = clean_user_input(text)
            
            # Geçerli kripto para sorgusu mu kontrol et
            if is_valid_crypto_query(cleaned_text):
                coin_id = get_coin_id(cleaned_text)
                
                if coin_id:
                    self.processing_users.add(user_id)
                    
                    # İşlem mesajı gönder
                    processing_msg = await update.message.reply_text("🔍 Fiyat bilgisi getiriliyor...")
                    
                    async with await get_crypto_api() as api:
                        coin_data = await api.get_coin_price(coin_id)
                        
                        if coin_data:
                            message = create_price_message(coin_data, cleaned_text)
                            await processing_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
                            logger.info(f"Text handler successful for '{cleaned_text}' by user {user_id}")
                        else:
                            await processing_msg.edit_text(
                                f"❌ '{text}' bulunamadı.\n"
                                "Desteklenen kripto paralar için /help komutunu kullanın."
                            )
                    
                    self.processing_users.discard(user_id)
            else:
                # Tanınmayan metin için yardım önerisi
                if len(text.split()) == 1 and len(text) > 2:  # Tek kelime ve yeterince uzun
                    await update.message.reply_text(
                        f"🤔 '{text}' tanınamadı.\n"
                        "Kripto para fiyatı için `/fiyat {text}` komutunu deneyin.\n"
                        "Veya /help ile desteklenen paraları görün."
                    )
        
        except Exception as e:
            logger.error(f"Error in text handler: {e}")
            # Sessizce geç, kullanıcıyı rahatsız etme
            pass
        
        finally:
            self.processing_users.discard(user_id)
