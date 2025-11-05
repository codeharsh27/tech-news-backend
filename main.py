from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import json, os, time
from datetime import datetime
from main_scraper import main as scrape_all_sites  # import your main scrape function

app = FastAPI(title="Tech News API")

# --- CORS so Flutter can access the API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cache config ---
CACHE_FILE = "news_cache.json"
CACHE_TTL = 1800  # 30 minutes (in seconds)

# --- Helpers for loading/saving cache ---
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

# --- Main /news endpoint ---
@app.get("/news")
def get_news():
    try:
        # Try to load from cache first
        cache = load_cache()
        if cache:
            last_updated = cache.get("last_updated", 0)
            age = time.time() - last_updated

            # Serve cached data if not older than 30 min
            if age < CACHE_TTL:
                print(f"[CACHE] Serving cached data (age: {int(age)} sec)")
                return cache

        # If no valid cache, scrape fresh data
        print("[UPDATE] Cache expired or missing - scraping fresh data...")
        
        # Import the main function here to avoid circular imports
        from main_scraper import main as scrape_all_sites
        
        # Set console encoding to UTF-8
        import sys
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        # Scrape fresh data
        articles = scrape_all_sites()
        
        if not isinstance(articles, list):
            print(f"[ERROR] scrape_all_sites() returned {type(articles)} instead of a list")
            if cache:
                print("[WARN] Returning cached data as fallback")
                return cache
            return {"error": "Failed to fetch articles, please try again later"}

        data = {
            "articles": articles,
            "last_updated": time.time(),
            "updated_at": datetime.now().isoformat(),
            "source": "fresh"
        }

        save_cache(data)
        print(f"[SUCCESS] Cache updated with {len(articles)} articles")
        return data
        
    except Exception as e:
        print(f"[ERROR] Error in get_news: {str(e)}")
        if cache:
            print("[WARN] Returning cached data as fallback")
            return cache
        return {"error": f"An error occurred: {str(e)}"}


# --- Background Scheduler ---
def background_refresh():
    print("[BACKGROUND] Refreshing cache...")
    try:
        articles = scrape_all_sites()
        data = {
            "articles": articles,
            "last_updated": time.time(),
            "updated_at": datetime.now().isoformat()
        }
        save_cache(data)
        print("[SUCCESS] Background cache refresh successful!")
    except Exception as e:
        print("[ERROR] Background job failed:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(background_refresh, "interval", minutes=30)
scheduler.start()

print("[INFO] Scheduler started - news will refresh every 30 minutes automatically.")
