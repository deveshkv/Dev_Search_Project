import os
import sqlite3
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh import index

# DB connection
conn = sqlite3.connect("content.db")
cursor = conn.cursor()
cursor.execute("SELECT title, url, content, language FROM articles")
rows = cursor.fetchall()

base_dir = "whoosh_index"
os.makedirs(base_dir, exist_ok=True)

# Predefined schema
schema = Schema(
    title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    url=ID(stored=True, unique=True),
    content=TEXT(stored=True, analyzer=StemmingAnalyzer())
)

# Group by language
lang_to_docs = {}
for title, url, content, lang in rows:
    if lang not in lang_to_docs:
        lang_to_docs[lang] = []
    lang_to_docs[lang].append((title, url, content))

# Build per-language index
for lang, docs in lang_to_docs.items():
    lang_dir = os.path.join(base_dir, lang)
    if not os.path.exists(lang_dir) or not index.exists_in(lang_dir):
        os.makedirs(lang_dir, exist_ok=True)
        ix = create_in(lang_dir, schema)
    else:
        ix = index.open_dir(lang_dir)

    writer = ix.writer()
    for title, url, content in docs:
        try:
            writer.add_document(title=title, url=url, content=title + " " + content)
            print(f"[✅] Indexed: {title} ({lang})")
        except Exception as e:
            print(f"[❌] Failed to index: {title} ({lang}) – {e}")
    writer.commit()

cursor.close()
conn.close()
