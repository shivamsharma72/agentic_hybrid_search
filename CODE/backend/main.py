"""
FastAPI Backend for Dual Ranking System
Modern REST API with async support
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import psycopg2

# Add parent directory to path to import from dual_ranking_system
# Now in CODE/backend, need to go up 3 levels to reach project root
sys.path.append(os.path.join(os.path.dirname(__file__), 'dual_ranking_system'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'rag_chatbot'))

from advanced_retriever import AdvancedRetriever
from feature_extractor import FeatureExtractor
from dual_ranker import DualRanker
import config as dual_config

# Import embedding model from RAG chatbot
from embedding_model import get_embedding_model

# Import query orchestrator and query-aware search
from query_orchestrator import get_orchestrator
from query_aware_search import QueryAwareSimilarity, create_query_aware_search_query

app = FastAPI(
    title="Dual Ranking API",
    description="Price vs. Sentiment Analysis API",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Next.js on port 3001 (3000 used by DOLOS)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
retriever = None
ranker = None
embedding_model = None
orchestrator = None

def initialize_services():
    """Initialize database connections, embedding model, and orchestrator"""
    global retriever, ranker, embedding_model, orchestrator
    
    print("🚀 Initializing backend services...")
    
    # Load embedding model (BLAIR-RoBERTa)
    print("📦 Loading BLAIR-RoBERTa embedding model...")
    embedding_model = get_embedding_model()
    print("✅ Embedding model loaded")
    
    # Initialize LangGraph query orchestrator
    print("🤖 Loading LangGraph Query Orchestrator...")
    orchestrator = get_orchestrator()
    print("✅ Query orchestrator loaded")
    
    # Initialize retriever and ranker
    retriever = AdvancedRetriever()
    ranker = DualRanker()
    
    print("✅ Backend initialized with Advanced Retriever + BLAIR + LangGraph")

def shutdown_services():
    """Close database connections"""
    global retriever, ranker
    if retriever:
        retriever.close()
    if ranker:
        ranker.close()
    print("👋 Backend shutdown")

# Initialize on import
initialize_services()

# Pydantic models for request/response
class ProductSearch(BaseModel):
    query: str
    limit: int = 10

class SemanticSearch(BaseModel):
    query: str
    limit: int = 10

class FindSimilarRequest(BaseModel):
    asin: str
    mode: str = "combined"  # "product" | "reviews" | "combined"
    k: int = 10

class AnalyzeSelectedRequest(BaseModel):
    asins: List[str]  # User-selected ASINs to analyze
    original_query: Optional[str] = None  # User's original search query for context

class QueryAnalysisRequest(BaseModel):
    query: str

class QueryAwareSearchRequest(BaseModel):
    original_query: str
    selected_asin: str
    mode: str = "query_aware"  # "query_aware" | "product_only" | "reviews_only"
    k: int = 10

class DualRankingRequest(BaseModel):
    asin: str
    k_neighbors: int = 10

class ProductInfo(BaseModel):
    asin: str
    title: str
    price: float
    average_rating: float
    rating_number: int
    category: Optional[str]
    similarity: Optional[float] = None

class Feature(BaseModel):
    feature_name: str
    positive_mentions: List[str]
    negative_mentions: List[str]
    positive_count: int
    negative_count: int
    net_sentiment: int

class FeatureExtraction(BaseModel):
    features: List[Feature]
    overall_summary: Dict[str, Any]

class RankedProduct(BaseModel):
    asin: str
    title: str
    price: float
    sentiment_score: float
    rank: int

class DualRankingResponse(BaseModel):
    original_product: ProductInfo
    price_ranking: List[RankedProduct]
    sentiment_ranking: List[RankedProduct]
    comparison: Dict[str, Any]
    all_products: Dict[str, Any]

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Dual Ranking API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        cur = retriever.conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "llm": "configured" if dual_config.OPENAI_API_KEY else "not configured"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/api/search")
async def search_products(search: ProductSearch):
    """Search for products by keyword"""
    try:
        cur = retriever.conn.cursor()
        cur.execute(f"""
            SELECT DISTINCT p.parent_asin, p.title, p.price, p.average_rating, 
                   COUNT(r.review_id) as actual_reviews
            FROM {dual_config.PRODUCTS_TABLE} p
            INNER JOIN {dual_config.REVIEWS_TABLE} r ON p.parent_asin = r.parent_asin
            WHERE p.title ILIKE %s
            AND p.blair_embedding IS NOT NULL
            AND p.price IS NOT NULL
            AND r.text IS NOT NULL
            AND LENGTH(r.text) > 50
            GROUP BY p.parent_asin, p.title, p.price, p.average_rating
            HAVING COUNT(r.review_id) >= 5
            ORDER BY COUNT(r.review_id) DESC
            LIMIT %s;
        """, (f"%{search.query}%", search.limit))
        
        results = cur.fetchall()
        cur.close()
        
        products = []
        for asin, title, price, rating, num_reviews in results:
            products.append({
                "asin": asin,
                "title": title,
                "price": float(price),
                "average_rating": float(rating),
                "rating_number": num_reviews,
                "category": None
            })
        
        return {
            "products": products,
            "total": len(products)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/semantic-search")
async def semantic_search(search: SemanticSearch):
    """
    Semantic search using natural language query
    Searches REVIEW embeddings to find products where users mention similar things
    """
    try:
        # TRUE Semantic Hybrid Search using BLAIR-RoBERTa
        print(f"🔍 Semantic search query: '{search.query}'")
        query_embedding = embedding_model.encode_query(search.query)
        print(f"✅ Query embedded (768-dim)")
        
        cur = retriever.conn.cursor()
        
        # HYBRID SEARCH: Products + Reviews
        query = f"""
            WITH product_matches AS (
                SELECT 
                    p.parent_asin,
                    p.title,
                    p.price,
                    p.average_rating,
                    p.rating_number,
                    1 - (p.blair_embedding <=> %s::vector) as product_similarity
                FROM {dual_config.PRODUCTS_TABLE} p
                WHERE p.blair_embedding IS NOT NULL
                AND p.price IS NOT NULL
                ORDER BY p.blair_embedding <=> %s::vector
                LIMIT 20
            ),
            review_matches AS (
                SELECT 
                    r.parent_asin,
                    COUNT(DISTINCT r.review_id) as matching_reviews,
                    AVG(1 - (r.blair_embedding <=> %s::vector)) as avg_review_similarity
                FROM {dual_config.REVIEWS_TABLE} r
                WHERE r.blair_embedding IS NOT NULL
                AND LENGTH(r.text) > 50
                GROUP BY r.parent_asin
                HAVING AVG(1 - (r.blair_embedding <=> %s::vector)) > 0.4
                ORDER BY avg_review_similarity DESC
                LIMIT 30
            ),
            combined AS (
                SELECT 
                    COALESCE(pm.parent_asin, rm.parent_asin) as parent_asin,
                    COALESCE(pm.title, p2.title) as title,
                    COALESCE(pm.price, p2.price) as price,
                    COALESCE(pm.average_rating, p2.average_rating) as average_rating,
                    COALESCE(pm.rating_number, p2.rating_number) as rating_number,
                    COALESCE(p2.images, '{{}}'::jsonb) as images,
                    COALESCE(pm.product_similarity, 0) as product_sim,
                    COALESCE(rm.avg_review_similarity, 0) as review_sim,
                    COALESCE(rm.matching_reviews, 0) as matching_reviews,
                    (0.4 * COALESCE(pm.product_similarity, 0) + 
                     0.6 * COALESCE(rm.avg_review_similarity, 0)) as hybrid_score
                FROM product_matches pm
                FULL OUTER JOIN review_matches rm ON pm.parent_asin = rm.parent_asin
                LEFT JOIN {dual_config.PRODUCTS_TABLE} p2 ON COALESCE(pm.parent_asin, rm.parent_asin) = p2.parent_asin
                WHERE pm.parent_asin IS NOT NULL OR rm.parent_asin IS NOT NULL
            )
            SELECT 
                parent_asin,
                title,
                price,
                average_rating,
                rating_number,
                images,
                product_sim,
                review_sim,
                matching_reviews,
                hybrid_score
            FROM combined
            ORDER BY hybrid_score DESC
            LIMIT %s;
        """
        
        cur.execute(query, [
            query_embedding, query_embedding,
            query_embedding, query_embedding,
            search.limit
        ])
        
        results = cur.fetchall()
        cur.close()
        
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, images, prod_sim, rev_sim, matching_revs, hybrid = row
            
            # Extract image URL
            image_url = None
            if images and isinstance(images, dict):
                for key in ['large', 'hi_res', 'thumb']:
                    if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                        image_url = images[key][0]
                        break
            
            if prod_sim > 0.7:
                reason = "Strong product title match"
            elif rev_sim > 0.7:
                reason = f"Found in {matching_revs} highly relevant reviews"
            elif rev_sim > 0.5:
                reason = f"Found in {matching_revs} relevant reviews"
            else:
                reason = "Product title match"
            
            products.append({
                "asin": asin,
                "title": title,
                "price": float(price) if price else None,
                "average_rating": float(rating) if rating else 0.0,
                "rating_number": num_reviews or 0,
                "image_url": image_url,
                "product_similarity": float(prod_sim) if prod_sim else 0.0,
                "review_similarity": float(rev_sim) if rev_sim else 0.0,
                "hybrid_score": float(hybrid) if hybrid else 0.0,
                "matching_reviews": int(matching_revs) if matching_revs else 0,
                "match_reason": reason
            })
        
        # For products with no reviews found, fetch their top 5 reviews
        for product in products:
            if product["matching_reviews"] == 0 and product["review_similarity"] == 0.0:
                print(f"📝 Fetching reviews for {product['asin']} (no reviews matched query)")
                
                try:
                    cur = retriever.conn.cursor()
                    cur.execute(f"""
                        SELECT 
                            1 - (blair_embedding <=> %s::vector) as similarity,
                            text,
                            title,
                            rating
                        FROM {dual_config.REVIEWS_TABLE}
                        WHERE parent_asin = %s
                        AND blair_embedding IS NOT NULL
                        AND LENGTH(text) > 50
                        ORDER BY blair_embedding <=> %s::vector
                        LIMIT 5
                    """, [query_embedding, product["asin"], query_embedding])
                    
                    review_rows = cur.fetchall()
                    cur.close()
                    
                    if review_rows:
                        # Calculate average similarity from fetched reviews
                        avg_sim = sum(float(r[0]) for r in review_rows) / len(review_rows)
                        product["review_similarity"] = avg_sim
                        product["matching_reviews"] = len(review_rows)
                        
                        # Recalculate hybrid score
                        product["hybrid_score"] = (
                            0.4 * product["product_similarity"] + 
                            0.6 * avg_sim
                        )
                        
                        print(f"✅ Found {len(review_rows)} reviews, avg similarity: {avg_sim:.3f}")
                except Exception as e:
                    print(f"⚠️  Failed to fetch reviews for {product['asin']}: {e}")
        
        # Re-sort by hybrid score after updating
        products.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        print(f"✅ Found {len(products)} products via hybrid search")
        
        return {
            "products": products,
            "total": len(products),
            "search_mode": "semantic_hybrid",
            "query_embedded": True
        }
        
    except Exception as e:
        print(f"❌ Semantic search error: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@app.post("/api/analyze-query")
async def analyze_query(request: QueryAnalysisRequest):
    """
    LangGraph Query Orchestrator
    Analyzes user query and provides refinement suggestions
    """
    try:
        print(f"🤖 Analyzing query: '{request.query}'")
        
        # Fetch available specs from database
        available_specs = {}
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    # Get unique categories (brands)
                    cur.execute(f"""
                        SELECT DISTINCT main_category
                        FROM {PRODUCTS_TABLE}
                        WHERE main_category IS NOT NULL AND main_category != ''
                        LIMIT 20
                    """)
                    brands = [row[0] for row in cur.fetchall() if row[0]]
                    
                    # Get price range
                    cur.execute(f"""
                        SELECT MIN(price), MAX(price)
                        FROM {PRODUCTS_TABLE}
                        WHERE price > 0
                    """)
                    price_result = cur.fetchone()
                    
                    available_specs = {
                        "brands": brands[:10] if brands else [],
                        "price_ranges": {
                            "min": int(price_result[0]) if price_result and price_result[0] else 200,
                            "max": int(price_result[1]) if price_result and price_result[1] else 2000
                        }
                    }
                    print(f"📊 Found {len(brands)} brands, price range: ${available_specs['price_ranges']['min']}-${available_specs['price_ranges']['max']}")
        except Exception as db_err:
            print(f"⚠️  Warning: Could not fetch available specs: {db_err}")
            available_specs = None
        
        # Run LangGraph orchestrator
        result = orchestrator.analyze(request.query)
        
        print(f"✅ Query analysis complete:")
        print(f"   Specific: {result['is_specific']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Specs detected: {result['specs_count']}")
        
        response = {
            "original_query": result["original_query"],
            "is_specific": result["is_specific"],
            "confidence": result["confidence"],
            "specs_count": result["specs_count"],
            "detected_specs": result["detected_specs"],
            "needs_refinement": result["needs_refinement"],
            "suggestions": result["suggestions"],
            "refined_query": result["refined_query"],
            "missing_specs": result["missing_specs"]
        }
        
        if available_specs:
            response["available_specs"] = available_specs
        
        return response
        
    except Exception as e:
        print(f"❌ Query analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")

@app.post("/api/query-aware-search")
async def query_aware_search(request: QueryAwareSearchRequest):
    """
    Query-Aware Similarity Search
    Finds similar products while keeping user's original query intent in mind
    """
    try:
        print(f"🎯 Query-aware search:")
        print(f"   Original query: '{request.original_query}'")
        print(f"   Selected product: {request.selected_asin}")
        print(f"   Mode: {request.mode}")
        
        # Embed original query
        query_embedding = embedding_model.encode_query(request.original_query)
        
        # Get selected product embeddings
        selected_product = retriever.get_product_by_asin(request.selected_asin)
        if not selected_product:
            raise HTTPException(status_code=404, detail=f"Product {request.selected_asin} not found")
        
        print(f"   Selected product: {selected_product.get('title', 'Unknown')}")
        
        # Convert embedding from string to list if needed
        product_embedding = selected_product.get('embedding')
        if not product_embedding:
            raise HTTPException(status_code=500, detail=f"Product {request.selected_asin} has no embedding")
        
        print(f"   Product embedding type: {type(product_embedding)}")
        
        if isinstance(product_embedding, str):
            # Parse string representation of array
            import json
            try:
                product_embedding = json.loads(product_embedding)
            except:
                # Try removing brackets and parsing
                product_embedding = [float(x) for x in product_embedding.strip('[]').split(',')]
        elif not isinstance(product_embedding, list):
            # If it's a numpy array or other type, convert to list
            product_embedding = list(product_embedding)
        
        print(f"   Product embedding length: {len(product_embedding)}")
        
        # Get average review embedding
        review_embedding = retriever.get_avg_review_embedding(request.selected_asin)
        if review_embedding and isinstance(review_embedding, str):
            import json
            review_embedding = json.loads(review_embedding.replace('[', '[').replace(']', ']'))
        elif review_embedding and not isinstance(review_embedding, list):
            review_embedding = list(review_embedding)
        
        # Create hybrid vector based on mode
        if request.mode == "query_aware":
            # Combine query + product + reviews
            hybrid_emb = QueryAwareSimilarity.create_hybrid_vector(
                query_embedding,
                product_embedding,
                review_embedding,
                weights={"query": 0.3, "product": 0.4, "reviews": 0.3}
            )
            search_type = "query_aware_hybrid"
        elif request.mode == "product_only":
            hybrid_emb = product_embedding
            search_type = "product_similarity"
        elif request.mode == "reviews_only" and review_embedding:
            hybrid_emb = review_embedding
            search_type = "review_similarity"
        else:
            hybrid_emb = QueryAwareSimilarity.create_hybrid_vector(
                query_embedding,
                product_embedding
            )
            search_type = "query_product_hybrid"
        
        # Search using hybrid vector
        cur = retriever.conn.cursor()
        
        query_sql = f"""
            SELECT 
                p.parent_asin,
                p.title,
                p.price,
                p.average_rating,
                p.rating_number,
                p.main_category,
                p.images,
                1 - (p.blair_embedding <=> %s::vector) as combined_similarity
            FROM {dual_config.PRODUCTS_TABLE} p
            WHERE p.blair_embedding IS NOT NULL
            AND p.price IS NOT NULL
            AND p.parent_asin != %s
            ORDER BY p.blair_embedding <=> %s::vector
            LIMIT %s;
        """
        
        cur.execute(query_sql, [hybrid_emb, request.selected_asin, hybrid_emb, request.k])
        results = cur.fetchall()
        cur.close()
        
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, category, images, similarity = row
            
            # Extract image URL
            image_url = None
            if images and isinstance(images, dict):
                for key in ['large', 'hi_res', 'thumb']:
                    if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                        image_url = images[key][0]
                        break
            
            # Generate explanation
            explanation = QueryAwareSimilarity.explain_similarity(
                request.original_query,
                selected_product['title'],
                title,
                {"query_similarity": similarity}  # Simplified for now
            )
            
            products.append({
                "asin": asin,
                "title": title,
                "price": float(price) if price else None,
                "average_rating": float(rating) if rating else 0.0,
                "rating_number": num_reviews or 0,
                "category": category,
                "image_url": image_url,
                "similarity": float(similarity) if similarity else 0.0,
                "match_reason": explanation
            })
        
        print(f"✅ Found {len(products)} query-aware results")
        
        return {
            "products": products,
            "total": len(products),
            "search_type": search_type,
            "original_query": request.original_query,
            "selected_product": selected_product['title']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Query-aware search error: {e}")
        print(f"   Full traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Query-aware search failed: {str(e)}")

@app.post("/api/find-similar")
async def find_similar(request: FindSimilarRequest):
    """
    Find similar products using different modes:
    - product: Similar by specs/category (product embeddings)
    - reviews: Similar by user experience (review embeddings)
    - combined: Best of both (dual search)
    """
    try:
        mode = request.mode.lower()
        
        if mode == "product":
            similar_products = retriever.find_similar_by_product(request.asin, k=request.k)
            search_type = "product_specifications"
            
        elif mode == "reviews":
            similar_products = retriever.find_similar_by_reviews(request.asin, k=request.k)
            search_type = "user_reviews"
            
        elif mode == "combined":
            similar_products = retriever.find_similar_combined(request.asin, k=request.k)
            search_type = "combined_product_and_reviews"
            
        else:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}. Use 'product', 'reviews', or 'combined'")
        
        # Format response
        products = []
        for p in similar_products:
            product_data = {
                "asin": p['asin'],
                "title": p['title'],
                "price": p['price'],
                "average_rating": p['average_rating'],
                "rating_number": p['rating_number'],
                "category": p.get('category'),
                "similarity": p.get('similarity', 0.0)
            }
            
            # Add mode-specific similarity scores
            if mode == "combined":
                product_data["product_similarity"] = p.get('product_similarity', 0.0)
                product_data["review_similarity"] = p.get('review_similarity', 0.0)
                product_data["combined_score"] = p.get('combined_score', 0.0)
            elif mode == "reviews":
                product_data["review_similarity"] = p.get('review_similarity', 0.0)
            
            products.append(product_data)
        
        return {
            "products": products,
            "total": len(products),
            "search_type": search_type,
            "mode": mode
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Find similar failed: {str(e)}")

def generate_recommendation_summary(asins, analyzed_products, price_ranking, sentiment_ranking, original_query):
    """
    Generate LLM-powered recommendation summary based on price ranges and user query
    Non-blocking - returns fallback message if generation fails
    """
    try:
        print(f"🤖 Generating AI recommendation for {len(asins)} laptops...")
        
        # Validate inputs
        if not original_query or not original_query.strip():
            original_query = "laptop shopping"
        
        # Group products by price ranges - safely
        prices = []
        for asin in asins:
            if asin in analyzed_products and analyzed_products[asin].get('price'):
                prices.append(analyzed_products[asin]['price'])
        
        if not prices or len(prices) < 2:
            print("⚠️ Not enough price data for recommendation")
            return {"text": "Compare the price and sentiment rankings above to find the best value for your needs."}
        
        min_price = min(prices)
        max_price = max(prices)
        price_range_size = (max_price - min_price) / 3 if max_price > min_price else 100
        
        # Count laptops in each tier
        budget_count = sum(1 for asin, p, r in price_ranking if p.get('price') and p['price'] <= min_price + price_range_size)
        mid_count = sum(1 for asin, p, r in price_ranking if p.get('price') and min_price + price_range_size < p['price'] <= min_price + 2*price_range_size)
        premium_count = sum(1 for asin, p, r in price_ranking if p.get('price') and p['price'] > min_price + 2*price_range_size)
        
        # Get top sentiment product safely
        top_sentiment = None
        top_sentiment_title = "N/A"
        top_sentiment_price = 0
        top_sentiment_score = 0
        if sentiment_ranking and len(sentiment_ranking) > 0:
            top_sentiment = sentiment_ranking[0][1]
            top_sentiment_title = top_sentiment.get('title', 'N/A')[:60]
            top_sentiment_price = top_sentiment.get('price', 0) or 0
            top_sentiment_score = top_sentiment.get('sentiment_score', 0) or 0
        
        # Get best price product safely
        best_price = None
        best_price_title = "N/A"
        best_price_price = 0
        best_price_score = 0
        if price_ranking and len(price_ranking) > 0:
            best_price = price_ranking[0][1]
            best_price_title = best_price.get('title', 'N/A')[:60]
            best_price_price = best_price.get('price', 0) or 0
            best_price_score = best_price.get('sentiment_score', 0) or 0
        
        # Build prompt for GPT
        prompt = f"""As a laptop recommendation expert, provide a brief 3-4 sentence recommendation.

USER'S SEARCH: "{original_query}"

PRICE ANALYSIS:
- Budget: ${min_price:.0f}-${min_price + price_range_size:.0f} ({budget_count} laptops)
- Mid: ${min_price + price_range_size:.0f}-${min_price + 2*price_range_size:.0f} ({mid_count} laptops)
- Premium: ${min_price + 2*price_range_size:.0f}+ ({premium_count} laptops)

TOP RATED: {top_sentiment_title} (${top_sentiment_price:.0f}, Score: {top_sentiment_score:.1f})

CHEAPEST: {best_price_title} (${best_price_price:.0f}, Score: {best_price_score:.1f})

Provide actionable advice addressing their needs and explaining value across price ranges."""

        # Call OpenAI
        from openai import OpenAI
        client = OpenAI(api_key=dual_config.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful laptop shopping assistant providing concise recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        recommendation_text = response.choices[0].message.content.strip()
        print(f"✅ Recommendation generated ({len(recommendation_text)} chars)")
        
        return {
            "text": recommendation_text,
            "price_tiers": {
                "budget": {"range": f"${min_price:.0f}-${min_price + price_range_size:.0f}", "count": budget_count},
                "mid": {"range": f"${min_price + price_range_size:.0f}-${min_price + 2*price_range_size:.0f}", "count": mid_count},
                "premium": {"range": f"${min_price + 2*price_range_size:.0f}+", "count": premium_count}
            }
        }
        
    except Exception as e:
        print(f"⚠️ Recommendation generation failed: {e}")
        import traceback
        traceback.print_exc()
        # Return fallback - don't crash the analysis
        return {"text": "Compare the price and sentiment rankings to find the best laptop for your needs. Consider both cost and user reviews when making your decision."}


@app.post("/api/analyze-selected")
async def analyze_selected(request: AnalyzeSelectedRequest):
    """
    Analyze only user-selected laptops (not all K neighbors)
    Runs dual ranking on the subset chosen by user
    """
    try:
        if not request.asins or len(request.asins) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Please select at least 2 laptops to analyze"
            )
        
        if len(request.asins) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 laptops can be analyzed at once"
            )
        
        # Use the existing dual ranker but on user-selected subset
        # We'll analyze each product
        print(f"\n🎯 Analyzing {len(request.asins)} user-selected laptops...")
        
        analyzed_products = ranker.analyze_products(request.asins)
        
        # Rank by price
        price_ranking = []
        for asin in sorted(analyzed_products.keys(), 
                          key=lambda x: analyzed_products[x]['price'] or float('inf')):
            price_ranking.append((asin, analyzed_products[asin], len(price_ranking) + 1))
        
        # Rank by sentiment
        sentiment_ranking = []
        for asin in sorted(analyzed_products.keys(),
                          key=lambda x: analyzed_products[x]['sentiment_score'], 
                          reverse=True):
            sentiment_ranking.append((asin, analyzed_products[asin], len(sentiment_ranking) + 1))
        
        # Find the first ASIN's position (treat as "original")
        original_asin = request.asins[0]
        price_rank = next((i for i, (a, _, r) in enumerate(price_ranking) if a == original_asin), -1) + 1
        sentiment_rank = next((i for i, (a, _, r) in enumerate(sentiment_ranking) if a == original_asin), -1) + 1
        
        # Format response (same as existing analyze endpoint)
        return {
            "original_product": {
                "asin": original_asin,
                "title": analyzed_products[original_asin]['title'],
                "price": float(analyzed_products[original_asin]['price']) if analyzed_products[original_asin]['price'] else None,
                "average_rating": float(analyzed_products[original_asin]['average_rating']),
                "rating_number": analyzed_products[original_asin]['rating_number'],
                "sentiment_score": analyzed_products[original_asin]['sentiment_score']
            },
            "price_ranking": [
                {
                    "asin": asin,
                    "title": data['title'],
                    "price": float(data['price']) if data['price'] else None,
                    "sentiment_score": data['sentiment_score'],
                    "rank": rank
                }
                for asin, data, rank in price_ranking
            ],
            "sentiment_ranking": [
                {
                    "asin": asin,
                    "title": data['title'],
                    "price": float(data['price']) if data['price'] else None,
                    "sentiment_score": data['sentiment_score'],
                    "rank": rank
                }
                for asin, data, rank in sentiment_ranking
            ],
            "comparison": {
                "original_asin": original_asin,
                "price_rank": price_rank,
                "sentiment_rank": sentiment_rank,
                "total_products": len(request.asins),
                "rank_difference": abs(price_rank - sentiment_rank),
                "better_value": sentiment_rank < price_rank
            },
            "recommendation": (
                generate_recommendation_summary(
                    request.asins,
                    analyzed_products,
                    price_ranking,
                    sentiment_ranking,
                    request.original_query
                ) if request.original_query else {
                    "text": "Compare the price and sentiment rankings to identify the best value."
                }
            ),
            "all_products": {
                asin: {
                    "title": data['title'],
                    "price": float(data['price']) if data['price'] else None,
                    "sentiment_score": data['sentiment_score'],
                    "num_reviews_fetched": data.get('num_reviews_fetched', 0),
                    "feature_extraction": data.get('feature_extraction', {})
                }
                for asin, data in analyzed_products.items()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/product/{asin}")
async def get_product(asin: str):
    """Get product details by ASIN"""
    try:
        product = retriever.get_product_by_asin(asin)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "asin": product['asin'],
            "title": product['title'],
            "price": float(product['price']) if product['price'] else None,
            "average_rating": float(product['average_rating']) if product['average_rating'] else 0.0,
            "rating_number": product['rating_number'] or 0,
            "category": product.get('category')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

@app.post("/api/analyze")
async def analyze_dual_ranking(request: DualRankingRequest):
    """Run dual ranking analysis"""
    try:
        # Run the dual ranking analysis
        results = ranker.run_dual_ranking(request.asin, k=request.k_neighbors)
        
        # Format response
        return {
            "original_product": {
                "asin": results['original_product']['asin'],
                "title": results['original_product']['title'],
                "price": float(results['original_product']['price']) if results['original_product']['price'] else None,
                "average_rating": float(results['original_product']['average_rating']),
                "rating_number": results['original_product']['rating_number'],
                "sentiment_score": results['original_product']['sentiment_score']
            },
            "price_ranking": [
                {
                    "asin": asin,
                    "title": data['title'],
                    "price": float(data['price']) if data['price'] else None,
                    "sentiment_score": data['sentiment_score'],
                    "rank": rank
                }
                for asin, data, rank in results['price_ranking']
            ],
            "sentiment_ranking": [
                {
                    "asin": asin,
                    "title": data['title'],
                    "price": float(data['price']) if data['price'] else None,
                    "sentiment_score": data['sentiment_score'],
                    "rank": rank
                }
                for asin, data, rank in results['sentiment_ranking']
            ],
            "comparison": results['comparison'],
            "all_products": {
                asin: {
                    "title": data['title'],
                    "price": float(data['price']) if data['price'] else None,
                    "sentiment_score": data['sentiment_score'],
                    "num_reviews_fetched": data.get('num_reviews_fetched', 0),
                    "feature_extraction": data.get('feature_extraction', {})
                }
                for asin, data in results['all_products'].items()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/sample-asins")
async def get_sample_asins():
    """Get sample ASINs for quick testing"""
    return {
        "samples": [
            {
                "asin": "B08N5WRWNW",
                "description": "Dell XPS 13 (2020+)",
                "category": "Premium Ultrabook"
            },
            {
                "asin": "B0C7BW1YQL",
                "description": "HP Laptop (2023)",
                "category": "Mid-range"
            },
            {
                "asin": "B07Q478DHY",
                "description": "Lenovo ThinkPad (2019+)",
                "category": "Business"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

