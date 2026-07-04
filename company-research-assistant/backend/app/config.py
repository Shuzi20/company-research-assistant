import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
SERPER_BASE_URL = "https://google.serper.dev"

# Crawler limits
MAX_PAGES_TO_CRAWL = 8
CRAWL_TIMEOUT_SECONDS = 8
MAX_CHARS_PER_PAGE = 2500

# Pages we actively look for while crawling
PRIORITY_PATH_KEYWORDS = [
    "about", "product", "service", "solution", "pricing", "contact", "team",
]

# Paths we skip outright
IGNORED_PATH_KEYWORDS = [
    "login", "signin", "signup", "register", "cart", "checkout",
    "privacy", "terms", "cookie", "careers/job", ".pdf", ".jpg", ".png",
]