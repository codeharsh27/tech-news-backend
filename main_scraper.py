from scrapper.techcrunch import scrape_techcrunch
from scrapper.verge import scrape_verge
from scrapper.wired import scrape_wired
import json
import traceback

def main():
    try:
        print("[DEBUG] Starting main scraper function")

        all_news = []

        # TechCrunch
        try:
            print("[DEBUG] Scraping TechCrunch...")
            tc_articles = scrape_techcrunch() or []
            print(f"[DEBUG] TechCrunch returned {len(tc_articles)} articles")
            all_news.extend(tc_articles)
        except Exception as e:
            print(f"[ERROR] TechCrunch scraper failed: {e}")

        # The Verge
        try:
            print("[DEBUG] Scraping The Verge...")
            verge_articles = scrape_verge() or []
            print(f"[DEBUG] The Verge returned {len(verge_articles)} articles")
            all_news.extend(verge_articles)
        except Exception as e:
            print(f"[ERROR] Verge scraper failed: {e}")

        # Wired
        try:
            print("[DEBUG] Scraping Wired...")
            wired_articles = scrape_wired() or []
            print(f"[DEBUG] Wired returned {len(wired_articles)} articles")
            all_news.extend(wired_articles)
        except Exception as e:
            print(f"[ERROR] Wired scraper failed: {e}")

        print(f"[SUCCESS] Total articles fetched: {len(all_news)}")

        # ✅ Always return a list, even if empty
        try:
            with open("all_news.json", "w", encoding="utf-8") as f:
                json.dump(all_news, f, indent=2, ensure_ascii=False)
            print("[SUCCESS] Saved to all_news.json")
        except Exception as e:
            print(f"[ERROR] Failed to save JSON: {e}")

        return all_news  # ✅ Always return list

    except Exception as e:
        print(f"[FATAL] Error in main(): {e}")
        traceback.print_exc()
        return []  # ✅ Never return None


if __name__ == "__main__":
    result = main()
    print(f"[FINAL] Scraper output: {len(result)} articles")
