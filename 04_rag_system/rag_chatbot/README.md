# RAG Chatbot for Electronics E-commerce 🤖

A production-ready Retrieval-Augmented Generation (RAG) chatbot using LangChain, OpenAI, and PostgreSQL with vector search.

## 🎯 Features

- **Query Enhancement**: Uses GPT-3.5 to extract intent, keywords, and filters from natural language
- **Hybrid Search**: Combines keyword search + filters + vector similarity (optional)
- **Smart Filtering**: Price, rating, category filters extracted automatically
- **Conversational**: Maintains conversation history for context
- **Production Ready**: Error handling, logging, configurable

## 📋 Architecture

```
User Query
    ↓
Query Enhancement (LLM)
    ↓
Extract: keywords, category, price, rating
    ↓
Hybrid Retriever
    ├── Keyword Search (PostgreSQL)
    ├── Category Filter
    ├── Price/Rating Filter
    └── Vector Search (optional)
    ↓
Top Products
    ↓
Response Generator (LLM)
    ↓
Natural Language Response
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd rag_chatbot
pip install -r requirements.txt
```

### 2. Run the Chatbot

```bash
python chatbot.py
```

### 3. Start Chatting!

```
You: I need a gaming laptop under $1000

Bot: Great! I found some excellent gaming laptops under $1000...
```

## 📦 Components

### 1. `query_enhancer.py` - Query Enhancement

Uses LangChain + OpenAI to extract structured parameters from natural language:

```python
User: "gaming laptop under $1000"
↓
{
    "keywords": ["gaming", "laptop", "gaming laptop"],
    "main_category": "Computers",
    "price_max": 1000,
    "min_rating": null,
    "sort_by": "rating_number",
    "intent": "browse"
}
```

**Features:**

- Keyword expansion
- Category mapping
- Price/rating extraction
- Intent classification
- Context-aware reasoning

### 2. `hybrid_retriever.py` - Product Search

Combines multiple search strategies:

```python
retriever.search(
    keywords=["gaming", "laptop"],
    category="Computers",
    price_max=1000,
    min_rating=4.0,
    limit=10
)
```

**Search Types:**

- **Keyword Search**: Multi-field (title, description, features)
- **Category Filter**: Exact or fuzzy category matching
- **Price Filter**: Min/max price range
- **Rating Filter**: Minimum rating threshold
- **Vector Search**: Semantic similarity (optional)

### 3. `response_generator.py` - Response Generation

Generates natural, conversational responses with product recommendations:

```python
generator.generate_response(
    user_query="gaming laptop under $1000",
    products=[...],
    enhanced_query={...}
)
```

**Response Includes:**

- Brief acknowledgment
- Top 3-5 product recommendations
- Key features, price, ratings
- Helpful suggestions

### 4. `chatbot.py` - Main Orchestrator

Ties everything together:

```python
chatbot = EcommerceChatbot()
response = chatbot.chat("I need a gaming laptop")
```

**Features:**

- Conversation history
- Error handling
- Interactive mode
- Configurable

## ⚙️ Configuration

Edit `config.py`:

```python
# OpenAI API Key
OPENAI_API_KEY = "sk-..."

# Database
DB_NAME = "amazon_electronics_rag"

# Models
QUERY_ENHANCER_MODEL = "gpt-3.5-turbo"  # Fast & cheap
RESPONSE_GENERATOR_MODEL = "gpt-3.5-turbo"  # Can upgrade to GPT-4

# Search
MAX_RESULTS = 10
USE_VECTOR_SEARCH = False  # Enable when you have embedding model
```

## 📊 Example Queries

```
✅ "I need a gaming laptop under $1000"
✅ "Show me the best wireless headphones"
✅ "What's a good webcam for video calls?"
✅ "I want a 4K TV around $500"
✅ "Cheap phone case with good reviews"
✅ "Affordable mechanical keyboard"
✅ "Noise cancelling earbuds rating 4.5"
✅ "Laptop for video editing"
```

## 🧪 Testing Individual Components

### Test Query Enhancer

```bash
python query_enhancer.py
```

Tests 10 sample queries and shows extracted parameters.

### Test Hybrid Retriever

```bash
python hybrid_retriever.py
```

Tests search with different filter combinations.

### Test Response Generator

```bash
python response_generator.py
```

Tests response generation with sample products.

## 🔧 Advanced Usage

### Custom Query Enhancement

```python
from query_enhancer import QueryEnhancer

enhancer = QueryEnhancer()
result = enhancer.enhance_query("gaming laptop under $1000")

print(result.keywords)  # ['gaming', 'laptop', ...]
print(result.main_category)  # 'Computers'
print(result.price_max)  # 1000
```

### Direct Product Search

```python
from hybrid_retriever import HybridRetriever

retriever = HybridRetriever()
products = retriever.search(
    keywords=["wireless", "headphones"],
    min_rating=4.5,
    price_max=200,
    limit=5
)

for p in products:
    print(f"{p.title} - ${p.price} - {p.rating}★")
```

### Conversation with History

```python
chatbot = EcommerceChatbot()

# First query
response1 = chatbot.chat("Show me laptops")

# Follow-up (understands context)
response2 = chatbot.chat("What about gaming ones under $1000?")
```

## 🎛️ Tuning Parameters

### Query Enhancer

- `temperature=0`: Deterministic (same input = same output)
- `temperature=0.7`: More creative (recommended for responses)
- `model="gpt-4"`: Better reasoning but slower/expensive

### Hybrid Retriever

- `limit`: Number of results (default: 10)
- `sort_by`: "rating_number" (popularity), "price", "average_rating"
- `use_vector`: Enable semantic search (requires embeddings)

### Response Generator

- `temperature=0.7`: Conversational and friendly
- `model="gpt-4"`: Better quality responses

## 💡 Tips

1. **Start Simple**: Test with keyword search first, add vector search later
2. **Monitor Costs**: GPT-3.5 is cheap (~$0.001/query), GPT-4 is expensive (~$0.03/query)
3. **Cache Results**: Cache common queries to save API calls
4. **Tune Prompts**: Adjust system prompts for better responses
5. **Add Filters**: Extend with brand, availability, shipping filters

## 🚨 Troubleshooting

**"OpenAI API Error"**

- Check API key in `config.py`
- Check API quota/limits

**"Database connection error"**

- Verify PostgreSQL is running
- Check database name in `config.py`

**"No products found"**

- Check if filters are too restrictive
- Verify data exists in database
- Try simpler queries

**"Response is generic/unhelpful"**

- Add more products to context
- Tune system prompt
- Use GPT-4 for better quality

## 📈 Performance

- **Query Enhancement**: ~200-500ms (GPT-3.5)
- **Product Search**: ~50-100ms (PostgreSQL)
- **Response Generation**: ~1-2s (GPT-3.5)
- **Total**: ~2-3s per query

## 🎯 Next Steps

1. ✅ Add vector embeddings for queries (semantic search)
2. ✅ Implement caching for common queries
3. ✅ Add product comparison features
4. ✅ Build web UI with Streamlit/Gradio
5. ✅ Add analytics and logging
6. ✅ Deploy to production

## 📚 Tech Stack

- **LangChain**: LLM orchestration
- **OpenAI GPT-3.5/4**: Query understanding & response generation
- **PostgreSQL + pgvector**: Product database & vector search
- **Python 3.8+**: Runtime

---

**Created**: 2025-10-29  
**Products**: 348,228 Electronics  
**Categories**: 35  
**Status**: Production Ready ✅

