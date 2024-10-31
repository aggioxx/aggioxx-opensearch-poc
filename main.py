from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from opensearchpy import OpenSearch
import requests
from transformers import AutoTokenizer, AutoModel
import torch

app = Flask(__name__)
CORS(app)

# OpenSearch connection details
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "Gui753357#"
INDEX_NAME = "news_articles"

# Initialize OpenSearch client
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

# Load BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def get_embedding(text):
    """
    Get BERT embedding for a given text.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()  # Average pooling
    return embedding.tolist()

def fetch_and_index_news():
    """
    Fetch news articles from News API and index them in OpenSearch.
    """
    params = {
        "apiKey": NEWS_API_KEY,
        "country": COUNTRY,
        "pageSize": 100
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        for i, article in enumerate(articles, start=1):
            title = article.get("title", "")
            description = article.get("description", "")

            if not isinstance(title, str) or not isinstance(description, str):
                print(f"Skipping article {i} due to invalid title or description")
                continue

            text = title + " " + description
            embedding = get_embedding(text)

            document = {
                "title": article["title"],
                "description": article["description"],
                "content": article["content"],
                "url": article["url"],
                "published_at": article["publishedAt"],
                "source": article["source"]["name"],
                "embedding": embedding
            }
            client.index(index=INDEX_NAME, body=document, id=i)
            print(f"Indexed article {i}: {document['title']}")
    else:
        print("Error fetching data from News API:", response.status_code, response.text)

def create_index_if_not_exists():
    """
    Create OpenSearch index with KNN mapping if it does not exist.
    """
    if not client.indices.exists(index=INDEX_NAME):
        index_body = {
            "settings": {
                "index": {
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "content": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 768
                    }
                }
            }
        }
        client.indices.create(index=INDEX_NAME, body=index_body)
        print(f"Created index '{INDEX_NAME}' with KNN enabled for embeddings.")

@app.route("/search", methods=["GET"])
def search_articles():
    """
    Search for articles using KNN on BERT embeddings.
    """
    query = request.args.get("query", "")
    if query:
        query_embedding = get_embedding(query)
        search_body = {
            "size": 5,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": 5
                    }
                }
            }
        }
        response = client.search(index=INDEX_NAME, body=search_body)
        return jsonify(response["hits"]["hits"])
    return jsonify([])

@app.route("/all", methods=["GET"])
def get_all_articles():
    """
    Get all articles from the OpenSearch index.
    """
    search_body = {"query": {"match_all": {}}}
    response = client.search(index=INDEX_NAME, body=search_body)
    return jsonify(response["hits"]["hits"])

@app.route("/")
def index():
    """
    Render the HTML search page.
    """
    return render_template("index.html")

if __name__ == "__main__":
    create_index_if_not_exists()
    existing_docs = client.count(index=INDEX_NAME)["count"]
    if existing_docs == 0:
        fetch_and_index_news()
        print("\nArticles indexed successfully.")
    else:
        print("Index already populated; skipping article indexing.")

    app.run(debug=True)