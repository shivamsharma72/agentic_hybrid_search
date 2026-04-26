"""
Enhanced Hybrid Retriever with BLAIR Cross-Modal Search + Graph Knowledge
Combines product + review embeddings with Graph DB constraints and enrichment
"""

import psycopg2
from typing import List, Optional, Dict, Any, Tuple
import os
from dotenv import load_dotenv
import config
from GraphRetriever import GraphRetriever

load_dotenv()

class Product:
    """Enhanced Product data structure with review evidence and graph insights"""
    def __init__(self, asin: str, title: str, price: float, rating: float, 
                 num_reviews: int, category: str, similarity: float = None, 
                 image_url: str = None, relevant_reviews: List[Dict] = None,
                 graph_insights: Dict[str, str] = None):
        self.asin = asin
        self.title = title
        self.price = price
        self.rating = rating
        self.num_reviews = num_reviews
        self.category = category
        self.similarity = similarity
        self.image_url = image_url
        self.relevant_reviews = relevant_reviews or []
        self.graph_insights = graph_insights or {}
        self.confidence_score = similarity  # Will be boosted by reviews
    
    def __repr__(self):
        return f"Product({self.asin}, {self.title[:50]}...)"
    
    def to_dict(self):
        return {
            "asin": self.asin,
            "title": self.title,
            "price": self.price,
            "rating": self.rating,
            "num_reviews": self.num_reviews,
            "category": self.category,
            "similarity": self.similarity,
            "confidence_score": self.confidence_score,
            "image_url": self.image_url,
            "relevant_reviews": self.relevant_reviews,
            "graph_insights": self.graph_insights
        }


class EnhancedHybridRetriever:
    """
    Enhanced retriever using BLAIR's cross-modal alignment + Graph DB
    """
    
    def __init__(self, db_name: str = None):
        self.db_name = db_name or config.DB_NAME
        self.db_user = config.DB_USER
        self.db_password = config.DB_PASSWORD
        self.db_host = config.DB_HOST
        self.db_port = config.DB_PORT
        self.conn = None
        self.connect()
        
        # Initialize Graph Retriever
        self.graph_retriever = GraphRetriever()
    
    def connect(self):
        """Connect to database using config settings"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            print(f"✅ Connected to Postgres: {self.db_name}")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
            
    def close(self):
        if self.conn:
            self.conn.close()
        if self.graph_retriever:
            self.graph_retriever.close()
    
    def extract_constraints(self, query: str) -> Dict[str, str]:
        """
        Simple keyword-based constraint extraction.
        In a real system, this would use an LLM.
        """
        filters = {}
        query_lower = query.lower()
        
        # RAM
        if "16gb" in query_lower: filters['ram'] = "16GB"
        elif "8gb" in query_lower: filters['ram'] = "8GB"
        elif "32gb" in query_lower: filters['ram'] = "32GB"
        
        # Price Category
        if "cheap" in query_lower or "budget" in query_lower: filters['price_category'] = "Cheap"
        elif "expensive" in query_lower or "premium" in query_lower: filters['price_category'] = "Expensive"
        
        # Color
        if "black" in query_lower: filters['color'] = "Black"
        elif "silver" in query_lower: filters['color'] = "Silver"
        
        # OS
        if "windows" in query_lower: filters['os'] = "Windows 10"
        elif "windows" in query_lower: filters['os'] = "Windows 11"
        elif "mac" in query_lower or "macos" in query_lower: filters['os'] = "Mac OS"
        elif "chrome" in query_lower: filters['os'] = "Chrome OS"
        
        # Storage Size
        if "256gb" in query_lower: filters['storage_size'] = "256GB"
        elif "512gb" in query_lower: filters['storage_size'] = "512GB"
        elif "1tb" in query_lower: filters['storage_size'] = "1TB"
        
        # Storage Type
        if "ssd" in query_lower: filters['storage_type'] = "SSD"
        elif "hdd" in query_lower: filters['storage_type'] = "HDD"
        
        # Weight
        if "lightweight" in query_lower or "portable" in query_lower: filters['weight'] = "Light"
        elif "heavy" in query_lower: filters['weight'] = "Heavy"
        elif "gaming" in query_lower: filters['weight'] = "Heavy" # Often implies heavy/gaming category
        
        return filters
    
    def search_unified(self, 
                      query_embedding: List[float],
                      query_text: str,
                      strategy: str = "balanced",
                      top_products: int = 20,
                      top_reviews: int = 50) -> Tuple[List[Product], Dict[str, Any]]:
        """
        Unified search using 3-Step Hybrid Approach:
        1. Graph Filter (Hard Constraints)
        2. Vector Search (Filtered Candidates)
        3. Graph Enrichment (Sentiment)
        """
        
        # Step 1: Graph Filtering
        constraints = self.extract_constraints(query_text)
        candidate_asins = []
        search_log = {
            "constraints": constraints,
            "filtered_count": 0,
            "vector_search_count": 0,
            "enrichment_count": 0
        }
        
        if constraints:
            print(f"🔍 Graph Constraints Detected: {constraints}")
            candidate_asins = self.graph_retriever.get_candidate_asins(constraints)
            search_log["filtered_count"] = len(candidate_asins)
            print(f"📉 Graph Filter reduced search space to {len(candidate_asins)} products")
            
            if not candidate_asins:
                print("⚠️ No products matched graph constraints. Falling back to full vector search.")
        
        # Step 2: Vector Search (with optional filter)
        products = self._search_products(
            query_embedding, 
            top_products,
            candidate_asins=candidate_asins if candidate_asins else None
        )
        
        # Search reviews (BLAIR ensures they cluster around relevant products!)
        reviews = self._search_reviews(
            query_embedding,
            top_reviews,
            candidate_asins=candidate_asins if candidate_asins else None
        )
        
        # Merge and enrich
        enriched_products = self._merge_results(products, reviews)
        
        # Step 3: Graph Enrichment
        enrichment_count = 0
        for product in enriched_products[:5]: # Enrich top 5
            insights = self.graph_retriever.enrich_product_sentiment(product.asin)
            product.graph_insights = insights
            enrichment_count += 1
            
        search_log["vector_search_count"] = len(products)
        search_log["enrichment_count"] = enrichment_count
            
        return enriched_products, search_log
    
    def _search_products(self, 
                        query_embedding: List[float],
                        limit: int,
                        candidate_asins: List[str] = None) -> List[Dict]:
        """Search products by vector similarity, optionally filtered by ASINs"""
        
        cur = self.conn.cursor()
        
        # Build WHERE clause
        where_clauses = ["blair_embedding IS NOT NULL"]
        params = []
        
        # Graph Filter
        if candidate_asins:
            placeholders = ','.join(['%s'] * len(candidate_asins))
            where_clauses.append(f"parent_asin IN ({placeholders})")
            params.extend(candidate_asins)
        
        # Execute query
        query = f"""
            SELECT 
                parent_asin,
                title,
                price,
                average_rating,
                rating_number,
                main_category,
                1 - (blair_embedding <=> %s::vector) as similarity,
                images
            FROM {config.PRODUCTS_TABLE}
            WHERE {' AND '.join(where_clauses)}
            ORDER BY blair_embedding <=> %s::vector
            LIMIT %s;
        """
        
        # Params: [query_embedding] + [candidates...] + [query_embedding] + [limit]
        # The query uses %s for vector first, then IN clause, then ORDER BY vector, then LIMIT
        all_params = [query_embedding] + params + [query_embedding, limit]
        
        cur.execute(query, all_params)
        results = cur.fetchall()
        cur.close()
        
        # Convert to dict
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, category, similarity, images = row
            
            # Extract image URL
            image_url = None
            if images and isinstance(images, dict):
                for key in ['large', 'hi_res', 'thumb']:
                    if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                        image_url = images[key][0]
                        break
            
            products.append({
                'asin': asin,
                'title': title,
                'price': price,
                'rating': rating,
                'num_reviews': num_reviews,
                'category': category,
                'similarity': float(similarity) if similarity else 0.0,
                'image_url': image_url
            })
        
        return products
    
    def _search_reviews(self,
                       query_embedding: List[float],
                       limit: int,
                       candidate_asins: List[str] = None) -> List[Dict]:
        """Search reviews by vector similarity"""
        
        cur = self.conn.cursor()
        
        # Build WHERE clause
        where_clauses = ["r.blair_embedding IS NOT NULL"]
        params = []
        
        # Graph Filter
        if candidate_asins:
            placeholders = ','.join(['%s'] * len(candidate_asins))
            where_clauses.append(f"r.parent_asin IN ({placeholders})")
            params.extend(candidate_asins)
        
        query = f"""
            SELECT 
                r.review_id,
                r.parent_asin,
                r.text,
                r.title as review_title,
                r.rating,
                r.helpful_vote,
                r.verified_purchase,
                1 - (r.blair_embedding <=> %s::vector) as similarity
            FROM {config.REVIEWS_TABLE} r
            WHERE {' AND '.join(where_clauses)}
            AND r.text IS NOT NULL
            AND LENGTH(r.text) > 50
            ORDER BY r.blair_embedding <=> %s::vector
            LIMIT %s;
        """
        
        # Params: [query_embedding] + [candidates...] + [query_embedding] + [limit]
        all_params = [query_embedding] + params + [query_embedding, limit]
        cur.execute(query, all_params)
        results = cur.fetchall()
        cur.close()
        
        # Convert to dict
        reviews = []
        for row in results:
            review_id, asin, text, title, rating, helpful, verified, similarity = row
            reviews.append({
                'review_id': review_id,
                'asin': asin,
                'text': text[:500] if text else '',
                'title': title,
                'rating': float(rating) if rating else 0.0,
                'helpful_vote': helpful or 0,
                'verified_purchase': verified,
                'similarity': float(similarity) if similarity else 0.0
            })
        
        return reviews
    
    def _merge_results(self, 
                      products: List[Dict], 
                      reviews: List[Dict]) -> List[Product]:
        """Merge products and reviews using BLAIR's alignment"""
        
        # Group reviews by product
        reviews_by_product = {}
        for review in reviews:
            asin = review['asin']
            if asin not in reviews_by_product:
                reviews_by_product[asin] = []
            reviews_by_product[asin].append(review)
        
        enriched_products = []
        for product in products:
            asin = product['asin']
            relevant_reviews = reviews_by_product.get(asin, [])
            
            # Calculate confidence boost
            review_boost = 0.0
            if relevant_reviews:
                avg_review_sim = sum(r['similarity'] for r in relevant_reviews) / len(relevant_reviews)
                count_factor = min(len(relevant_reviews) / 10, 1.0)
                review_boost = avg_review_sim * count_factor * 0.15
            
            prod_obj = Product(
                asin=asin,
                title=product['title'],
                price=product['price'],
                rating=product['rating'],
                num_reviews=product['num_reviews'],
                category=product['category'],
                similarity=product['similarity'],
                image_url=product['image_url'],
                relevant_reviews=relevant_reviews
            )
            
            prod_obj.confidence_score = product['similarity'] + review_boost
            enriched_products.append(prod_obj)
        
        # Sort by confidence score
        enriched_products.sort(key=lambda p: p.confidence_score, reverse=True)
        
        return enriched_products

    def _get_products_by_asins(self, asins: List[str]) -> List[Dict]:
        """Get product details for a list of ASINs"""
        if not asins:
            return []
        
        cur = self.conn.cursor()
        placeholders = ','.join(['%s'] * len(asins))
        query = f"""
            SELECT parent_asin, title, price, average_rating, rating_number, main_category, images
            FROM {config.PRODUCTS_TABLE}
            WHERE parent_asin IN ({placeholders});
        """
        cur.execute(query, asins)
        results = cur.fetchall()
        cur.close()
        
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, category, images = row
            image_url = None
            if images and isinstance(images, dict):
                for key in ['large', 'hi_res', 'thumb']:
                    if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                        image_url = images[key][0]
                        break
            products.append({
                'asin': asin, 'title': title, 'price': price, 'rating': rating, 
                'num_reviews': num_reviews, 'category': category, 'image_url': image_url
            })
        return products
