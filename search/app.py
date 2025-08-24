from flask import Flask, request, render_template, redirect, url_for, session
from lang_config import UI_LABELS
from langdetect import detect, DetectorFactory
from whoosh.qparser import QueryParser, OrGroup
from whoosh.index import open_dir
from collections import Counter
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management

DetectorFactory.seed = 0

# -------- Language Detection ----------
def detect_language(text):
    try:
        text = text.strip()
        if len(text) < 3:
            raise Exception("Too short")
        lang = detect(text)
        if lang not in UI_LABELS:
            return "en"
        return lang
    except:
        return "en"

# -------- Language Setter Route ----------
@app.route('/set_lang/<lang_code>')
def set_language(lang_code):
    if lang_code in UI_LABELS:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('home'))

# -------- Home ----------
@app.route('/')
def home():
    lang = session.get("lang", "en")
    labels = UI_LABELS[lang]
    return render_template("search.html", query="", results=[], suggestion=None, labels=labels, lang=lang, page=1)

# -------- Search ----------
@app.route('/search')
def search():
    query_str = request.args.get('q', '').strip()
    page = int(request.args.get("page", 1))
    lang = session.get("lang", "en")
    results_list = []
    suggestion = None
    used_suggestion = False  # <-- NEW FLAG

    if not query_str:
        return render_template('search.html', query=query_str, results=results_list, suggestion=None, labels=UI_LABELS[lang], lang=lang, page=page)

    detected_lang = detect_language(query_str)
    index_path = f"whoosh_index/{detected_lang}"

    if not os.path.exists(index_path):
        return render_template('search.html', query=query_str, results=[], suggestion=None, labels=UI_LABELS[lang], lang=lang, page=page)

    try:
        ix = open_dir(index_path)
        with ix.searcher() as searcher:
            qp = QueryParser("content", schema=ix.schema, group=OrGroup)
            query = qp.parse(query_str)
            results = searcher.search(query, limit=10)

            if len(results) == 0:
                corrector = searcher.corrector("content")
                words = query_str.split()
                suggestions = [corrector.suggest(w, limit=1) for w in words]
                corrected = [s[0] if s else w for s, w in zip(suggestions, words)]
                if corrected != words:
                    suggestion = " ".join(corrected)
                    used_suggestion = True  # <-- ENABLE FLAG
                    query = qp.parse(suggestion)  # <-- RE-PARSE QUERY
                    results = searcher.search(query, limit=10)  # <-- NEW SEARCH
                    query_str = suggestion  # <-- UPDATE QUERY STRING
            for hit in results:
                results_list.append({
                    "title": hit.get("title", "No Title"),
                    "url": hit.get("url", "#"),
                    "snippet": hit.highlights("content") or "..."
                })

    except Exception as e:
        print(f"[❌] Search failed: {e}")
        return render_template('search.html', query=query_str, results=[], suggestion=None, labels=UI_LABELS[lang], lang=lang, page=page)

    return render_template(
        'search.html',
        query=query_str,
        results=results_list,
        suggestion=suggestion if used_suggestion else None,
        labels=UI_LABELS[lang],
        lang=lang,
        page=page
    )

    # return render_template('search.html', query=query_str, results=results_list, suggestion=suggestion, labels=UI_LABELS[lang], lang=lang, page=page)

# -------- Trending Queries ----------
def get_trending_queries(top_n=5):
    try:
        with open("logs/queries.txt", "r", encoding="utf-8") as f:
            queries = f.readlines()
        counter = Counter([q.strip() for q in queries if q.strip()])
        return counter.most_common(top_n)
    except:
        return []

# -------- Entry ----------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
