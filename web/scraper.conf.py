
from TripAdvisorScraper.config.config import Path

SCRAP_REVIEWS = False
SCRAP_DEALS = False
SCRAP_GEO = True
OUTPUT_REVIEWS_JSON = None
OUTPUT_DEALS_JSON = None
OUTPUT_HOTEL_INFO_JSON = None
OUTPUT_GEO_JSON = None
OUTPUT_BULK_JSON = None
OUTPUT_SQLITE = Path('./data/tripadvisor.db')
ENABLE_DEBUG = True
OUTPUT_SCRAP_LOG = Path('./log/scraper.log')
OUTPUT_SQLITE_LOG = False
OUTPUT_DEBUG_INFO_TO_STDOUT = False
GOOGLE_MAPS_API_KEY = 'AIzaSyDXA3qp5PF2-83FjtIjMuzHE48z0O7Unsk'
