from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os, time, json
from supabase import create_client, Client
from main_scraper import main as scrape_all_sites

# --- Init FastAPI ---
app = FastAPI(title="Tech News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Supabase setup ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CACHE_TTL = 1800  # 30 min

# --- Helpers ---
def load_cache():
    try:
        response = supabase.table("news_cache").select("*").order("updated_at", desc=True).limit(1).execute()
        if response.data:
            row = response.data[0]
            age = time.time() - row["last_updated"]
            print(f"[DB] Cache age: {int(age)} sec")
            return row if age < CACHE_TTL else None
    except Exception as e:
        print(f"[ERROR] load_cache(): {e}")
    return None

def save_cache(data):
    try:
        supabase.table("news_cache").insert({
            "data": data,
            "last_updated": time.time(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        print(f"[DB] Cache saved to Supabase ({len(data['articles'])} articles)")
    except Exception as e:
        print(f"[ERROR] save_cache(): {e}")

# --- API route ---
@app.get("/news")
def get_news():
    cache = load_cache()
    if cache:
        print("[CACHE] Serving data from Supabase cache")
        return cache["data"]

    print("[UPDATE] Cache expired — scraping fresh data...")
    articles = scrape_all_sites()
    data = {
        "articles": articles,
        "last_updated": time.time(),
        "updated_at": datetime.utcnow().isoformat()
    }
    save_cache(data)
    return data

# --- Background refresh every 30 min ---
def background_refresh():
    print("[JOB] Refreshing cache...")
    articles = scrape_all_sites()
    data = {
        "articles": articles,
        "last_updated": time.time(),
        "updated_at": datetime.utcnow().isoformat()
    }
    save_cache(data)
    print("[JOB] Cache updated")

scheduler = BackgroundScheduler()
scheduler.add_job(background_refresh, "interval", minutes=30)
scheduler.start()
print("[INFO] Scheduler started (Supabase version)")
