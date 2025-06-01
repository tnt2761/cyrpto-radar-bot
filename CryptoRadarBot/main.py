#!/usr/bin/env python3
"""
Türk Kripto Takip Botu - Ana dosya
Turkish Cryptocurrency Tracking Telegram Bot - Main file
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from bot_handlers import BotHandlers

# Logging yapılandırması
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hata yakalayıcı fonksiyon"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        )

def main():
    """Ana fonksiyon - Botu başlatır"""
    try:
        # Bot uygulamasını oluştur
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Handler sınıfını başlat
        handlers = BotHandlers()
        
        # Komut handler'larını ekle
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("fiyat", handlers.price_command))
        application.add_handler(CommandHandler("btc", handlers.btc_command))
        application.add_handler(CommandHandler("eth", handlers.eth_command))
        application.add_handler(CommandHandler("top10", handlers.top10_command))
        application.add_handler(CommandHandler("ara", handlers.search_command))
        application.add_handler(CommandHandler("yukselenler", handlers.top_gainers_command))
        
        # Metin mesajları için handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))
        
        # Hata handler'ını ekle
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Kripto Radar Botu başlatılıyor...")
        
        # Botu çalıştır
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Bot başlatılırken hata oluştu: {e}")
        raise

if __name__ == "__main__":
    main()