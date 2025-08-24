import sqlite3

conn = sqlite3.connect("content.db")
cursor = conn.cursor()

cursor.execute("SELECT title, url, content, language FROM articles ORDER BY timestamp DESC LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    title, url, content, language = row
    print("\n---")
    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"Language: {language}")
    print(f"Content Snippet: {content[:300]}...")

cursor.execute("SELECT language, COUNT(*) FROM articles GROUP BY language")
print(cursor.fetchall())
print(f"[📥] Language: {language}")
print(f"[📥] Title: {title}")
print(f"[📥] Snippet: {content[:150]}")
