"""
Hybrid Retriever: Combines keyword search + vector search + filtering
"""

import psycopg2
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Product:
    """Product data structure"""
    def __init__(self, asin: str, title: str, price: float, rating: float, 
                 num_reviews: int, category: str, similarity: float = None, image_url: str = None):
        self.asin = asin
        self.title = title
        self.price = price
        self.rating = rating
        self.num_reviews = num_reviews
        self.category = category
        self.similarity = similarity
        self.image_url = image_url
    
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
            "image_url": self.image_url
        }


class HybridRetriever:
    """Retrieve products using hybrid search"""
    
    def __init__(self, db_name: str = None):
        self.db_name = db_name or os.getenv("DB_NAME", "amazon_electronics_rag")
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(f"dbname={self.db_name}")
            print(f"✅ Connected to database: {self.db_name}")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def search(self, 
               keywords: List[str],
               category: Optional[str] = None,
               price_min: Optional[float] = None,
               price_max: Optional[float] = None,
               min_rating: Optional[float] = None,
               sort_by: str = "rating_number",
               limit: int = 10,
               use_vector: bool = False,
               query_embedding: Optional[List[float]] = None) -> List[Product]:
        """
        Hybrid search combining filters and vector similarity
        
        Args:
            keywords: List of keywords to search
            category: Category filter
            price_min: Minimum price
            price_max: Maximum price
            min_rating: Minimum rating
            sort_by: Sort field (rating_number, price, average_rating)
            limit: Number of results
            use_vector: Use vector similarity search
            query_embedding: Query embedding (required if use_vector=True)
        """
        cur = self.conn.cursor()
        
        # Build WHERE clause - RELAXED STRATEGY
        # Only strict requirement: must have embedding
        where_clauses = ["blair_embedding IS NOT NULL"]
        params = []
        
        # OPTIONAL keyword filtering (only if semantic search is OFF)
        # If vector search is ON, rely on semantic similarity instead
        if not use_vector and keywords and len(keywords) > 0:
            # Relaxed: match ANY keyword in ANY field
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(
                    "(title ILIKE %s OR description ILIKE %s OR features ILIKE %s)"
                )
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            
            # At least ONE keyword should match
            if keyword_conditions:
                where_clauses.append(f"({' OR '.join(keyword_conditions)})")
        
        # SOFT filters (applied but not strict) - will be used for ranking later
        # Category: Don't filter, just use for semantic search
        # Price: Only apply if VERY specific (both min and max)
        if price_min is not None and price_max is not None:
            where_clauses.append("(price IS NULL OR (price >= %s AND price <= %s))")
            params.extend([price_min, price_max])
        
        # Rating: Only apply if explicitly high threshold (4.5+)
        if min_rating is not None and min_rating >= 4.5:
            where_clauses.append("average_rating >= %s")
            params.append(min_rating)
        
        # Build query
        if use_vector and query_embedding:
            # Vector similarity search with proper parameter ordering
            cur.execute("SET ivfflat.probes = 50;")  # Use IVFFlat index
            
            # Use numbered placeholders to avoid parameter ordering issues
            # First two %s are for embeddings in SELECT and ORDER BY
            # Then come all the WHERE clause params
            # Last is LIMIT
            query_with_placeholders = f"""
                SELECT 
                    parent_asin,
                    title,
                    price,
                    average_rating,
                    rating_number,
                    main_category,
                    1 - (blair_embedding <=> %s::vector) as similarity,
                    images
                FROM products
                WHERE {' AND '.join(where_clauses)}
                ORDER BY blair_embedding <=> %s::vector
                LIMIT %s;
            """
            
            # CRITICAL: Params must match the order of %s in the SQL
            # 1st %s: embedding in SELECT (similarity calculation)
            # Then: all WHERE clause params (keywords, category, price, rating)
            # 2nd embedding %s: embedding in ORDER BY
            # Last %s: LIMIT
            all_params = [query_embedding] + params + [query_embedding, limit]
        else:
            # Keyword-only search
            query = f"""
                SELECT 
                    parent_asin,
                    title,
                    price,
                    average_rating,
                    rating_number,
                    main_category,
                    NULL as similarity,
                    images
                FROM products
                WHERE {' AND '.join(where_clauses)}
                ORDER BY {sort_by} DESC NULLS LAST
                LIMIT %s;
            """
            all_params = params + [limit]
        
        cur.execute(query_with_placeholders if use_vector and query_embedding else query, all_params)
        results = cur.fetchall()
        cur.close()
        
        # Convert to Product objects
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, category, similarity, images = row
            
            # Extract first image URL from JSONB
            image_url = None
            if images:
                try:
                    # Format: {"large": ["url"], "thumb": ["url"], "hi_res": ["url"]}
                    if isinstance(images, dict):
                        # Try large first (medium quality), then hi_res, then thumb
                        for key in ['large', 'hi_res', 'thumb']:
                            if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                                image_url = images[key][0]  # Get first URL from array
                                break
                except Exception as e:
                    print(f"Image parsing error for ASIN {asin}: {e}")
                    pass
            
            # Debug: Print first few products with image status
            if len(products) < 3:
                print(f"Product {asin}: image_url = {image_url[:50] if image_url else 'None'}")
            
            products.append(Product(asin, title, price, rating, num_reviews, category, similarity, image_url))
        
        return products
    
    def get_product_by_asin(self, asin: str) -> Optional[Product]:
        """Get a single product by ASIN"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT parent_asin, title, price, average_rating, rating_number, main_category
            FROM products
            WHERE parent_asin = %s;
        """, (asin,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            asin, title, price, rating, num_reviews, category = result
            return Product(asin, title, price, rating, num_reviews, category)
        return None
    
    def get_reviews_for_products(self, product_asins: List[str], limit_per_product: int = 3) -> Dict[str, List[Dict]]:
        """
        Get top reviews for multiple products
        
        Args:
            product_asins: List of product ASINs
            limit_per_product: Number of reviews per product (default 3)
            
        Returns:
            Dict mapping ASIN to list of review dicts
        """
        if not product_asins:
            return {}
        
        cur = self.conn.cursor()
        
        reviews_by_product = {}
        
        for asin in product_asins:
            # Get top helpful reviews (highest rating first, then most helpful)
            cur.execute("""
                SELECT 
                    rating,
                    title,
                    text,
                    verified_purchase,
                    helpful_vote
                FROM reviews
                WHERE parent_asin = %s
                AND text IS NOT NULL
                AND LENGTH(text) > 50
                ORDER BY 
                    rating DESC,
                    helpful_vote DESC NULLS LAST
                LIMIT %s;
            """, (asin, limit_per_product))
            
            reviews = []
            for row in cur.fetchall():
                rating, title, text, verified, helpful = row
                reviews.append({
                    'rating': rating,
                    'title': title,
                    'text': text[:500] if text else '',  # Limit text length
                    'verified_purchase': verified,
                    'helpful_vote': helpful or 0
                })
            
            if reviews:
                reviews_by_product[asin] = reviews
        
        cur.close()
        return reviews_by_product
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Test the retriever
if __name__ == "__main__":
    retriever = HybridRetriever()
    
    print("=" * 80)
    print("TESTING HYBRID RETRIEVER")
    print("=" * 80)
    
    # Test 1: Keyword search with filters
    print("\n🔍 Test 1: Gaming laptops under $1000")
    results = retriever.search(
        keywords=["gaming", "laptop"],
        category="Computers",
        price_max=1000,
        min_rating=4.0,
        limit=5
    )
    
    for i, product in enumerate(results, 1):
        print(f"\n{i}. {product.title[:70]}")
        print(f"   Price: ${product.price:.2f} | Rating: {product.rating:.1f}★ ({product.num_reviews:,} reviews)")
    
    # Test 2: Keyword search only
    print("\n" + "=" * 80)
    print("🔍 Test 2: Wireless headphones")
    results = retriever.search(
        keywords=["wireless", "headphones"],
        min_rating=4.5,
        limit=5
    )
    
    for i, product in enumerate(results, 1):
        print(f"\n{i}. {product.title[:70]}")
        print(f"   Price: ${product.price:.2f} | Rating: {product.rating:.1f}★ ({product.num_reviews:,} reviews)")
    
    retriever.close()

