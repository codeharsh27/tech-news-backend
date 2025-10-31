from scrapper.techcrunch import scrape_techcrunch
from scrapper.verge import scrape_verge
from scrapper.wired import scrape_wired
import json

def main():
    all_news = []
    techcrunch_articles = scrape_techcrunch()
    verge_articles = scrape_verge()
    wired_articles = scrape_wired()

    print(f"TechCrunch articles: {len(techcrunch_articles)}")
    print(f"Verge articles: {len(verge_articles)}")
    print(f"Wired articles: {len(wired_articles)}")

    all_news.extend(techcrunch_articles)
    all_news.extend(verge_articles)
    all_news.extend(wired_articles)

    print(f"✅ Total articles fetched: {len(all_news)}")

    with open("all_news.json", "w") as f:
        json.dump(all_news, f, indent=2)

    print("✅ Saved to all_news.json")

if __name__ == "__main__":
    main()
