from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scrapper.techcrunch import scrape_techcrunch
from scrapper.verge import scrape_verge
from scrapper.wired import scrape_wired

app = FastAPI(title="Tech News API", version="1.0")

# Allow Flutter app to access this API (important for mobile/web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🚀 Tech News API is running!"}


@app.get("/news")
def get_all_news():
    """
    Combines news from all scrapers into a single response.
    """
    news = []
    news.extend(scrape_techcrunch())
    news.extend(scrape_verge())
    news.extend(scrape_wired())
    return {"count": len(news), "articles": news}
