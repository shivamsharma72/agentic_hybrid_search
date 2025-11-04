"""
Enhanced Hybrid Retriever with BLAIR Cross-Modal Search
Combines product + review embeddings for better recommendations
"""

import psycopg2
from typing import List, Optional, Dict, Any, Tuple
import os
from dotenv import load_dotenv
import config

load_dotenv()

class Product:
    """Enhanced Product data structure with review evidence"""
    def __init__(self, asin: str, title: str, price: float, rating: float, 
                 num_reviews: int, category: str, similarity: float = None, 
                 image_url: str = None, relevant_reviews: List[Dict] = None):
        self.asin = asin
        self.title = title
        self.price = price
        self.rating = rating
        self.num_reviews = num_reviews
        self.category = category
        self.similarity = similarity
        self.image_url = image_url
        self.relevant_reviews = relevant_reviews or []
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
            "relevant_reviews": self.relevant_reviews
        }


class EnhancedHybridRetriever:
    """
    Enhanced retriever using BLAIR's cross-modal alignment
    Searches BOTH products and reviews in same vector space
    """
    
    def __init__(self, db_name: str = None):
        self.db_name = db_name or config.DB_NAME
        self.db_user = config.DB_USER
        self.db_password = config.DB_PASSWORD
        self.db_host = config.DB_HOST
        self.db_port = config.DB_PORT
        self.conn = None
        self.connect()
    
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
            print(f"✅ Connected to database: {self.db_name} (user: {self.db_user})")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def search_unified(self, 
                      query_embedding: List[float],
                      strategy: str = "balanced",
                      category: Optional[str] = None,
                      price_min: Optional[float] = None,
                      price_max: Optional[float] = None,
                      min_rating: Optional[float] = None,
                      top_products: int = 20,
                      top_reviews: int = 50) -> List[Product]:
        """
        Unified search using BLAIR's cross-modal alignment
        
        Args:
            query_embedding: Query vector (768-dim BLAIR embedding)
            strategy: "product_focused", "balanced", or "review_focused"
            category: Category filter
            price_min: Minimum price
            price_max: Maximum price  
            min_rating: Minimum rating
            top_products: Number of products to search
            top_reviews: Number of reviews to search
            
        Returns:
            List of Product objects enriched with relevant reviews
        """
        
        # Adjust limits based on strategy
        if strategy == "product_focused":
            top_products, top_reviews = 20, 30
        elif strategy == "review_focused":
            top_products, top_reviews = 15, 60
        else:  # balanced
            top_products, top_reviews = 20, 50
        
        # Search products
        products = self._search_products(
            query_embedding, 
            top_products,
            category,
            price_min,
            price_max,
            min_rating
        )
        
        # Search reviews (BLAIR ensures they cluster around relevant products!)
        reviews = self._search_reviews(
            query_embedding,
            top_reviews,
            category
        )
        
        # Merge and enrich
        enriched_products = self._merge_results(products, reviews)
        
        return enriched_products
    
    def _search_products(self, 
                        query_embedding: List[float],
                        limit: int,
                        category: Optional[str] = None,
                        price_min: Optional[float] = None,
                        price_max: Optional[float] = None,
                        min_rating: Optional[float] = None) -> List[Dict]:
        """Search products by vector similarity"""
        
        cur = self.conn.cursor()
        
        # Build WHERE clause
        where_clauses = ["blair_embedding IS NOT NULL"]
        params = []
        
        # Category filter (if provided)
        if category:
            where_clauses.append("main_category ILIKE %s")
            params.append(f"%{category}%")
        
        # Price filter
        if price_min is not None and price_max is not None:
            where_clauses.append("(price IS NULL OR (price >= %s AND price <= %s))")
            params.extend([price_min, price_max])
        elif price_max is not None:
            where_clauses.append("(price IS NULL OR price <= %s)")
            params.append(price_max)
        
        # Rating filter
        if min_rating is not None:
            where_clauses.append("average_rating >= %s")
            params.append(min_rating)
        
        # Execute query
        try:
            # Try to optimize IVFFlat index (if it exists)
            cur.execute("SET ivfflat.probes = 50;")
        except:
            # Rollback and continue if it fails
            conn.rollback()
        
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
                       category: Optional[str] = None) -> List[Dict]:
        """
        Search reviews by vector similarity
        
        BLAIR ensures these reviews cluster around semantically similar products!
        """
        
        cur = self.conn.cursor()
        
        # Build WHERE clause
        where_clauses = ["r.blair_embedding IS NOT NULL"]
        params = []
        
        # Optional category filter (via product join)
        category_join = ""
        if category:
            category_join = f"INNER JOIN {config.PRODUCTS_TABLE} p ON r.parent_asin = p.parent_asin"
            where_clauses.append("p.main_category ILIKE %s")
            params.append(f"%{category}%")
        
        # Execute query
        try:
            # Try to optimize IVFFlat index (if it exists)
            cur.execute("SET ivfflat.probes = 50;")
        except:
            # Rollback and continue if it fails
            conn.rollback()
        
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
            {category_join}
            WHERE {' AND '.join(where_clauses)}
            AND r.text IS NOT NULL
            AND LENGTH(r.text) > 50
            ORDER BY r.blair_embedding <=> %s::vector
            LIMIT %s;
        """
        
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
                'text': text[:500] if text else '',  # Truncate for context
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
        """
        Merge products and reviews using BLAIR's alignment
        
        Strategy:
        1. Group reviews by product ASIN
        2. Enrich products with their relevant reviews
        3. Boost confidence score based on review evidence
        4. Add products discovered through reviews
        """
        
        # Group reviews by product
        reviews_by_product = {}
        for review in reviews:
            asin = review['asin']
            if asin not in reviews_by_product:
                reviews_by_product[asin] = []
            reviews_by_product[asin].append(review)
        
        # Track which ASINs are already in products
        product_asins = set(p['asin'] for p in products)
        
        # Enrich products with reviews
        enriched_products = []
        for product in products:
            asin = product['asin']
            relevant_reviews = reviews_by_product.get(asin, [])
            
            # Calculate confidence boost from reviews
            # More relevant reviews = higher confidence
            review_boost = 0.0
            if relevant_reviews:
                # Average review similarity × count factor
                avg_review_sim = sum(r['similarity'] for r in relevant_reviews) / len(relevant_reviews)
                count_factor = min(len(relevant_reviews) / 10, 1.0)  # Cap at 10 reviews
                review_boost = avg_review_sim * count_factor * 0.15  # Up to 15% boost
            
            # Create Product object
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
            
            # Boost confidence score
            prod_obj.confidence_score = product['similarity'] + review_boost
            
            enriched_products.append(prod_obj)
        
        # Find products discovered through reviews (not in top products)
        discovered_asins = set(reviews_by_product.keys()) - product_asins
        
        if discovered_asins:
            # Get product details for discovered ASINs
            discovered_products = self._get_products_by_asins(list(discovered_asins)[:5])  # Limit to top 5
            
            for product in discovered_products:
                asin = product['asin']
                relevant_reviews = reviews_by_product.get(asin, [])
                
                # For discovered products, use avg review similarity as base
                if relevant_reviews:
                    avg_review_sim = sum(r['similarity'] for r in relevant_reviews) / len(relevant_reviews)
                    
                    prod_obj = Product(
                        asin=asin,
                        title=product['title'],
                        price=product['price'],
                        rating=product['rating'],
                        num_reviews=product['num_reviews'],
                        category=product['category'],
                        similarity=avg_review_sim * 0.9,  # Slightly lower than direct match
                        image_url=product.get('image_url'),
                        relevant_reviews=relevant_reviews
                    )
                    
                    prod_obj.confidence_score = avg_review_sim * 0.9
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
            SELECT 
                parent_asin,
                title,
                price,
                average_rating,
                rating_number,
                main_category,
                images
            FROM {config.PRODUCTS_TABLE}
            WHERE parent_asin IN ({placeholders});
        """
        
        cur.execute(query, asins)
        results = cur.fetchall()
        cur.close()
        
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, category, images = row
            
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
                'image_url': image_url
            })
        
        return products
    
    def get_product_by_asin(self, asin: str) -> Optional[Product]:
        """Get a single product by ASIN"""
        cur = self.conn.cursor()
        cur.execute(f"""
            SELECT parent_asin, title, price, average_rating, rating_number, main_category, images
            FROM {config.PRODUCTS_TABLE}
            WHERE parent_asin = %s;
        """, (asin,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            asin, title, price, rating, num_reviews, category, images = result
            
            # Extract image URL
            image_url = None
            if images and isinstance(images, dict):
                for key in ['large', 'hi_res', 'thumb']:
                    if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                        image_url = images[key][0]
                        break
            
            return Product(asin, title, price, rating, num_reviews, category, image_url=image_url)
        return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Test the enhanced retriever
if __name__ == "__main__":
    from embedding_model import EmbeddingModel
    
    print("="*80)
    print("TESTING ENHANCED HYBRID RETRIEVER WITH BLAIR CROSS-MODAL SEARCH")
    print("="*80)
    
    # Initialize
    retriever = EnhancedHybridRetriever()
    embedding_model = EmbeddingModel()
    
    # Test query
    query = "lightweight gaming laptop with good battery life and quiet fans"
    print(f"\n🔍 Query: '{query}'")
    
    # Generate embedding
    query_embedding = embedding_model.embed_query(query)
    print(f"✅ Generated embedding: {len(query_embedding)} dimensions")
    
    # Search with different strategies
    strategies = ["balanced", "product_focused", "review_focused"]
    
    for strategy in strategies:
        print(f"\n{'='*80}")
        print(f"📊 Strategy: {strategy.upper()}")
        print(f"{'='*80}")
        
        results = retriever.search_unified(
            query_embedding=query_embedding,
            strategy=strategy,
            top_products=15,
            top_reviews=40
        )
        
        for i, product in enumerate(results[:5], 1):
            print(f"\n{i}. {product.title[:70]}")
            print(f"   ASIN: {product.asin}")
            print(f"   Price: ${product.price:.2f}" if product.price else "   Price: N/A")
            print(f"   Rating: {product.rating:.2f}★ ({product.num_reviews:,} reviews)")
            print(f"   Similarity: {product.similarity:.3f}")
            print(f"   Confidence: {product.confidence_score:.3f}")
            print(f"   Relevant Reviews: {len(product.relevant_reviews)}")
            
            # Show top relevant review
            if product.relevant_reviews:
                top_review = product.relevant_reviews[0]
                print(f"   📝 Top Review: '{top_review['title']}' ({top_review['rating']}★)")
                print(f"      Similarity: {top_review['similarity']:.3f}")
                print(f"      Text: {top_review['text'][:100]}...")
    
    retriever.close()
    print(f"\n{'='*80}\n")

