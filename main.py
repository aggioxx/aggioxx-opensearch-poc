from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from opensearchpy import OpenSearch
import requests

app = Flask(__name__)
CORS(app)

# OpenSearch connection details
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "Gui753357#"
INDEX_NAME = "news_articles"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
    use_ssl=True,
    verify_certs=False,
)

# News API configuration
NEWS_API_KEY = "b2b94788e9c347e7997340556f912f08"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
COUNTRY = "us"

# Create index if not exists
if not client.indices.exists(index=INDEX_NAME):
    client.indices.create(index=INDEX_NAME)
    print(f"Created index '{INDEX_NAME}'")

# Fetch and index news articles
def fetch_and_index_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "country": COUNTRY,
        "pageSize": 100
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        for i, article in enumerate(articles, start=1):
            document = {
                "title": article["title"],
                "description": article["description"],
                "content": article["content"],
                "url": article["url"],
                "published_at": article["publishedAt"],
                "source": article["source"]["name"],
            }
            client.index(index=INDEX_NAME, body=document, id=i)
            print(f"Indexed article {i}: {document['title']}")
    else:
        print("Error fetching data from News API:", response.status_code, response.text)

# Route to fetch search results
@app.route("/search", methods=["GET"])
def search_articles():
    query = request.args.get("query", "")
    if query:
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description", "content"]
                }
            }
        }
        response = client.search(index=INDEX_NAME, body=search_body)
        return jsonify(response["hits"]["hits"])
    return jsonify([])

# Route to get all documents
@app.route("/all", methods=["GET"])
def get_all_articles():
    search_body = {"query": {"match_all": {}}}
    response = client.search(index=INDEX_NAME, body=search_body)
    return jsonify(response["hits"]["hits"])

# Route to render the HTML search page
@app.route("/")
def index():
    return render_template("index.html")

# Fetch and index articles when running
if __name__ == "__main__":
    fetch_and_index_news()
    print("\nArticles indexed successfully.")
    app.run(debug=True)
