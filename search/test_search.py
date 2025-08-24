from whoosh.qparser import QueryParser
from whoosh.index import open_dir

ix = open_dir("index")
print("[✅] Index opened successfully.")

qp = QueryParser("content", schema=ix.schema)

with ix.searcher() as searcher:
    query = qp.parse("india")  # Or try "*"
    results = searcher.search(query, limit=5)

    print(f"[ℹ️] Found {len(results)} results for query.")

    for result in results:
        print("\n--- Result ---")
        print("Title:", result['title'])
        print("URL:", result['url'])
        print("Snippet:", result.highlights("content"))