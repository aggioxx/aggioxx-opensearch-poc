from math import atan2

import requests
from opensearchpy import OpenSearch

# OpenSearch connection details
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200  # Corrected port
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "Gui753357#"
INDEX_NAME = "news_articles"

# News API configuration
NEWS_API_KEY = "b2b94788e9c347e7997340556f912f08"  # Replace with your actual News API key
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
COUNTRY = "us"

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
    use_ssl=True,  # Enable SSL
    verify_certs=False,  # Disable SSL certificate verification (not recommended for production)
)

# Step 1: Create an index for news articles (if it doesn't exist)
if not client.indices.exists(index=INDEX_NAME):
    client.indices.create(index=INDEX_NAME)
    print(f"Created index '{INDEX_NAME}'")

# Step 2: Fetch news articles from News API
def fetch_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "country": COUNTRY,
        "pageSize": 100
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        print(response.json().get("articles", []))
        return response.json().get("articles", [])
    else:
        print("Error fetching data from News API:", response.status_code, response.text)
        return []

# Step 3: Index articles into OpenSearch
def index_articles(articles):
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

# Step 4: Search for articles in OpenSearch
def search_articles(query):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "description", "content"]
            }
        }
    }
    response = client.search(index=INDEX_NAME, body=search_body)
    return response

# Main Execution
if __name__ == "__main__":
    # Fetch and index articles
    articles = fetch_news()
    if articles:
        index_articles(articles)
        print("\nArticles indexed successfully.")

        # Sample search query
        query = "linkedin"
        search_results = search_articles(query)

        print(f"\nSearch Results for query '{query}':")
        for hit in search_results["hits"]["hits"]:
            print(f"Title: {hit['_source']['title']}")
            print(f"Description: {hit['_source']['description']}")
            print(f"URL: {hit['_source']['url']}\n")
    else:
        print("No articles fetched to index.")