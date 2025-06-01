"""
CoinGecko API entegrasyonu
CoinGecko API integration for cryptocurrency data
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from config import COINGECKO_API_BASE, API_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)

class CryptoAPI:
    """CoinGecko API ile kripto para verilerini yöneten sınıf"""
    
    def __init__(self):
        self.base_url = COINGECKO_API_BASE
        self.timeout = API_TIMEOUT
        self.session = None
        
    async def __aenter__(self):
        """Async context manager giriş"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager çıkış"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """API isteği yapan yardımcı fonksiyon"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        logger.warning(f"API request failed with status {response.status}")
                        return None
                        
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                    
            except Exception as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                    
        return None
    
    async def get_coin_price(self, coin_id: str) -> Optional[Dict]:
        """Belirli bir kripto paranın fiyat bilgilerini getirir"""
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd,try',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        data = await self._make_request('simple/price', params)
        
        if data and coin_id in data:
            return data[coin_id]
        return None
    
    async def get_top_cryptocurrencies(self, limit: int = 10) -> Optional[List[Dict]]:
        """En popüler kripto paraları getirir"""
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        return await self._make_request('coins/markets', params)
    
    async def search_cryptocurrency(self, query: str) -> Optional[List[Dict]]:
        """Kripto para arama yapar"""
        params = {'query': query}
        data = await self._make_request('search', params)
        
        if data and 'coins' in data:
            return data['coins'][:5]  # İlk 5 sonuç
        return None
    
    async def get_coin_details(self, coin_id: str) -> Optional[Dict]:
        """Kripto para detaylarını getirir"""
        params = {
            'localization': False,
            'tickers': False,
            'market_data': True,
            'community_data': False,
            'developer_data': False,
            'sparkline': False
        }
        
        return await self._make_request(f'coins/{coin_id}', params)

# Global API instance
async def get_crypto_api():
    """CryptoAPI instance döndürür"""
    return CryptoAPI()
