# News Article Search Engine

A semantic search engine for news articles using OpenSearch, BERT embeddings, and Flask. This application fetches recent news articles, indexes them with embeddings for semantic search, and provides a simple web interface to search through the articles.

## Features

- Fetches latest news articles from News API
- Indexes articles in OpenSearch with BERT embeddings
- Supports semantic search using KNN vector search
- Simple web interface for searching articles
- Combined semantic and keyword search for better results

## Technologies Used

- **Backend**: Python, Flask
- **Search Engine**: OpenSearch
- **Machine Learning**: Hugging Face Transformers (BERT)
- **Frontend**: HTML, JavaScript
- **Data Source**: News API

## Setup and Installation

### Prerequisites

- Python 3.7+
- OpenSearch (running locally or accessible instance)
- News API key

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd news-search-engine
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-cors opensearch-py requests transformers torch
   ```

3. Configure OpenSearch:
    - Ensure OpenSearch is running (default: localhost:9200)
    - Set up admin credentials in `.env` file

4. Set your News API key:
    - Get a key from [News API](https://newsapi.org/)
    - Update `NEWS_API_KEY` in `main.py`

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the search bar to find news articles by keywords or concepts

## API Endpoints

- `GET /search?query=<search-term>`: Search articles using semantic search
- `GET /all`: Retrieve all indexed articles

## Configuration

You can modify the following parameters in `main.py`:

- `OPENSEARCH_HOST` and `OPENSEARCH_PORT`: OpenSearch connection details
- `OPENSEARCH_USER` and `OPENSEARCH_PASS`: Authentication credentials
- `INDEX_NAME`: The name of the OpenSearch index to use
- `NEWS_API_KEY`: Your News API key
- `COUNTRY`: The country code for News API (default: "us")

## Note

This project is for educational purposes. Ensure you comply with News API's terms of service when using their data.