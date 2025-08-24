import sqlite3
import requests
from bs4 import BeautifulSoup
from langdetect import detect
import pandas as pd
import os

# === CSV Path ===
CSV_PATH = r"E:\Projects\Dev_Search_Project\data\sites.csv"

# === DB setup ===
DB_PATH = os.path.join("data", "content.db")
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    url TEXT UNIQUE,
    content TEXT,
    tags TEXT,
    language TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def insert_article(title, url, content, tags, language):
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO articles (title, url, content, tags, language)
            VALUES (?, ?, ?, ?, ?)
        """, (title, url, content, tags, language))
        conn.commit()
        print(f"[✅] Inserted: {title} ({language})")
    except Exception as e:
        print(f"[❌] Insert error for {url}: {e}")

# === Custom scraping logic ===
def extract_and_scrape(domain_url, base_domain, lang_hint="unknown"):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(domain_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        links = set()
        for a in soup.find_all("a", href=True):
            href = a['href']
            if not href.startswith("http"):
                href = base_domain + href
            if base_domain in href and ("/article" in href or href.endswith(".html")):
                links.add(href)

        print(f"[🔍] Found {len(links)} links on {domain_url}")

        count = 0
        for link in list(links)[:5]:  # Limit to 5 articles
            try:
                r = requests.get(link, headers=headers, timeout=10)
                s = BeautifulSoup(r.content, "html.parser")
                title_tag = s.find("title")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                paragraphs = s.find_all("p")
                content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                if not content:
                    continue
                language = detect(content)
                insert_article(title, link, content, "", language)
                count += 1
            except Exception as inner_e:
                print(f"[⚠️] Could not process article: {link} - {inner_e}")
        print(f"[✅] Done scraping {count} articles from {domain_url}\n")
    except Exception as e:
        print(f"[❌] Failed to load homepage {domain_url}: {e}")

# === Load Sites from CSV ===
def load_sites_from_csv(csv_path=CSV_PATH):
    """
    CSV columns: homepage,base,lang
    """
    if not os.path.exists(csv_path):
        print(f"[❌] CSV file not found at {csv_path}")
        return []

    df = pd.read_csv(csv_path)
    sites_list = []
    for _, row in df.iterrows():
        sites_list.append({
            "homepage": row["homepage"].strip(),
            "base": row["base"].strip(),
            "lang": row.get("lang", "en").strip()
        })
    return sites_list

# === Start scraping ===
if __name__ == "__main__":
    sites = load_sites_from_csv()
    if not sites:
        print("[⚠️] No sites loaded. Please check your CSV file.")
    for site in sites:
        extract_and_scrape(site["homepage"], site["base"], site["lang"])

    cursor.close()
    conn.close()
