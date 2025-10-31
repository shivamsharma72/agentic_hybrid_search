"""
BM25 Keyword Search for Product Retrieval

Uses PostgreSQL's built-in text search (ts_vector) with BM25-like ranking
for efficient keyword-based search without external dependencies.

Key Features:
- Tokenization with stemming (English)
- TF-IDF style ranking (PostgreSQL ts_rank)
- Multi-field search (title, description, features)
- Query expansion (synonyms, brand alternatives)
"""

import psycopg2
import re
from typing import List, Optional, Dict, Set
from dataclasses import dataclass

# Brand alternatives for "I like X, suggest Y" queries
BRAND_ALTERNATIVES = {
    'bose': ['sony', 'sennheiser', 'jbl', 'beats', 'audio-technica', 'shure'],
    'sony': ['bose', 'sennheiser', 'jbl', 'panasonic', 'lg'],
    'apple': ['samsung', 'microsoft', 'dell', 'hp', 'lenovo', 'asus'],
    'samsung': ['apple', 'sony', 'lg', 'oneplus', 'google'],
    'beats': ['bose', 'sony', 'sennheiser', 'jbl', 'audio-technica'],
    'jbl': ['bose', 'sony', 'beats', 'ultimate ears', 'anker'],
}

# Product category keywords for better filtering
CATEGORY_KEYWORDS = {
    'audio': ['headphones', 'earbuds', 'speakers', 'soundbar', 'audio', 'sound', 'music'],
    'laptop': ['laptop', 'notebook', 'chromebook', 'macbook', 'ultrabook'],
    'phone': ['phone', 'smartphone', 'iphone', 'android'],
    'tv': ['tv', 'television', 'display', 'monitor', 'screen'],
    'camera': ['camera', 'dslr', 'mirrorless', 'webcam', 'gopro'],
}

@dataclass
class BM25SearchQuery:
    """Parsed and expanded search query"""
    original_query: str
    search_terms: List[str]
    excluded_brands: Set[str]
    alternative_brands: Set[str]
    category_hints: List[str]
    intent: str  # 'alternative', 'similar', 'specific', 'browse'


class BM25Retriever:
    """BM25-based keyword search using PostgreSQL full-text search"""
    
    def __init__(self, db_name: str = "amazon_electronics_rag"):
        self.db_name = db_name
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(f"dbname={self.db_name}")
            print(f"✅ BM25 Retriever connected to: {self.db_name}")
        except Exception as e:
            print(f"❌ BM25 connection error: {e}")
            raise
    
    def parse_query(self, query: str) -> BM25SearchQuery:
        """
        Parse user query and extract intent, brands, alternatives
        
        Handles queries like:
        - "I like bose, suggest alternatives for audio devices"
        - "headphones similar to sony but not sony"
        - "laptops like macbook but cheaper"
        """
        query_lower = query.lower()
        
        # Detect intent
        intent = 'browse'
        if any(word in query_lower for word in ['like', 'similar', 'alternative', 'instead of', 'not']):
            if any(word in query_lower for word in ['alternative', 'suggest', 'other', 'different']):
                intent = 'alternative'
            else:
                intent = 'similar'
        elif any(word in query_lower for word in ['specific', 'exact', 'this', 'that']):
            intent = 'specific'
        
        # Extract excluded brands (e.g., "I like bose" → exclude bose)
        excluded_brands = set()
        alternative_brands = set()
        
        # Pattern: "I like X" or "similar to X"
        like_patterns = [
            r'i like (\w+)',
            r'similar to (\w+)',
            r'like (\w+) but',
            r'instead of (\w+)',
        ]
        
        for pattern in like_patterns:
            matches = re.findall(pattern, query_lower)
            for brand in matches:
                excluded_brands.add(brand)
                # Get alternatives
                if brand in BRAND_ALTERNATIVES:
                    alternative_brands.update(BRAND_ALTERNATIVES[brand])
        
        # Explicitly excluded brands (e.g., "not sony")
        not_patterns = [
            r'not (\w+)',
            r'no (\w+)',
            r'except (\w+)',
            r'but not (\w+)',
        ]
        
        for pattern in not_patterns:
            matches = re.findall(pattern, query_lower)
            excluded_brands.update(matches)
        
        # Extract category hints
        category_hints = []
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                category_hints.append(category)
        
        # Extract search terms (remove filler words)
        filler_words = {
            'i', 'like', 'want', 'need', 'suggest', 'recommend', 'show', 'find',
            'me', 'good', 'best', 'for', 'from', 'other', 'brands', 'alternative',
            'similar', 'but', 'not', 'and', 'or', 'the', 'a', 'an', 'to', 'of'
        }
        
        # Tokenize and clean
        tokens = re.findall(r'\b\w+\b', query_lower)
        search_terms = [
            token for token in tokens 
            if token not in filler_words and len(token) > 2
        ]
        
        # Add category keywords to search terms
        for category in category_hints:
            search_terms.extend(CATEGORY_KEYWORDS[category][:3])  # Top 3 keywords
        
        # Remove duplicates while preserving order
        search_terms = list(dict.fromkeys(search_terms))
        
        return BM25SearchQuery(
            original_query=query,
            search_terms=search_terms,
            excluded_brands=excluded_brands,
            alternative_brands=alternative_brands,
            category_hints=category_hints,
            intent=intent
        )
    
    def search_bm25(
        self,
        query: str,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        min_rating: Optional[float] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        BM25-style keyword search using PostgreSQL ts_rank
        
        Args:
            query: Natural language query
            category: Filter by category
            price_min: Minimum price
            price_max: Maximum price
            min_rating: Minimum rating
            limit: Number of results
            
        Returns:
            List of product dictionaries with BM25 scores
        """
        # Parse query
        parsed = self.parse_query(query)
        
        print(f"\n🔍 BM25 Query Analysis:")
        print(f"   Search terms: {parsed.search_terms}")
        print(f"   Excluded brands: {parsed.excluded_brands}")
        print(f"   Alternative brands: {parsed.alternative_brands}")
        print(f"   Category hints: {parsed.category_hints}")
        print(f"   Intent: {parsed.intent}")
        
        if not parsed.search_terms:
            print("⚠️  No valid search terms extracted!")
            return []
        
        cur = self.conn.cursor()
        
        # Build ts_query string for PostgreSQL full-text search
        # Join with '|' (OR) for better recall
        ts_query_string = ' | '.join(parsed.search_terms)
        
        # Build WHERE clauses
        where_clauses = []
        params = []
        
        # Build search terms string (used multiple times)
        search_terms_str = ' '.join(parsed.search_terms)
        
        # 1. Text search using to_tsvector and plainto_tsquery
        # This uses PostgreSQL's built-in stemming and ranking
        where_clauses.append("""
            (
                to_tsvector('english', COALESCE(title, '') || ' ' || 
                                       COALESCE(description, '') || ' ' || 
                                       COALESCE(features, ''))
                @@ plainto_tsquery('english', %s)
            )
        """)
        params.append(search_terms_str)
        
        # 2. Exclude specified brands (from store field)
        if parsed.excluded_brands:
            for brand in parsed.excluded_brands:
                where_clauses.append("LOWER(store) NOT LIKE %s")
                params.append(f"%{brand}%")
        
        # 3. Prefer alternative brands (will boost in scoring)
        # Don't filter, just prepare for scoring
        
        # 4. Category filter
        if category:
            where_clauses.append("main_category = %s")
            params.append(category)
        
        # 5. Price filter
        if price_min is not None:
            where_clauses.append("price >= %s")
            params.append(price_min)
        if price_max is not None:
            where_clauses.append("price <= %s")
            params.append(price_max)
        
        # 6. Rating filter
        if min_rating is not None:
            where_clauses.append("average_rating >= %s")
            params.append(min_rating)
        
        # Build scoring expression
        # ts_rank gives BM25-like scoring
        # We also boost alternative brands
        
        alternative_brands_sql = ""
        alternative_brand_params = []
        if parsed.alternative_brands:
            # Create CASE statement to boost alternative brands
            # Use parameterized queries to avoid % escaping issues
            brand_conditions = []
            for brand in parsed.alternative_brands:
                brand_conditions.append("LOWER(store) LIKE %s")
                alternative_brand_params.append(f"%{brand}%")
            alternative_brands_sql = f"""
                + CASE 
                    WHEN {' OR '.join(brand_conditions)} THEN 0.5
                    ELSE 0 
                  END
            """
        
        # Full query with BM25 ranking
        # Note: We use the same search terms for both WHERE and SELECT scoring
        query_sql = f"""
            SELECT 
                parent_asin,
                title,
                price,
                average_rating,
                rating_number,
                main_category,
                store,
                images,
                (
                    ts_rank(
                        to_tsvector('english', COALESCE(title, '') || ' ' || 
                                               COALESCE(description, '') || ' ' || 
                                               COALESCE(features, '')),
                        plainto_tsquery('english', %s)
                    )
                    * LOG(rating_number + 1)  -- Boost by popularity
                    {alternative_brands_sql}  -- Boost alternative brands
                ) as bm25_score
            FROM products
            WHERE {' AND '.join(where_clauses)}
            ORDER BY bm25_score DESC, rating_number DESC
            LIMIT %s;
        """
        
        # Parameters: 
        # 1. search_terms for SELECT ts_rank scoring
        # 2. alternative_brand_params for CASE statement (if any)
        # 3. all WHERE params (search_terms, brand_exclusions, filters)
        # 4. limit
        all_params = [search_terms_str] + alternative_brand_params + params + [limit]
        
        # Debug (can be removed in production)
        # print(f"\n🐛 DEBUG: {len(all_params)} params for SQL with {query_sql.count('%s')} placeholders")
        
        cur.execute(query_sql, all_params)
        results = cur.fetchall()
        cur.close()
        
        # Convert to dictionaries
        products = []
        for row in results:
            asin, title, price, rating, num_reviews, cat, store, images, bm25_score = row
            
            # Extract image URL
            image_url = None
            if images:
                try:
                    if isinstance(images, dict):
                        for key in ['large', 'hi_res', 'thumb']:
                            if key in images and isinstance(images[key], list) and len(images[key]) > 0:
                                image_url = images[key][0]
                                break
                except:
                    pass
            
            products.append({
                'asin': asin,
                'title': title,
                'price': price,
                'rating': rating,
                'num_reviews': num_reviews,
                'category': cat,
                'store': store,
                'image_url': image_url,
                'bm25_score': float(bm25_score),
                'similarity': float(bm25_score) / 10.0  # Normalize to 0-1 range (approx)
            })
        
        print(f"✅ Found {len(products)} results")
        if products:
            print(f"   Top BM25 scores: {[p['bm25_score'] for p in products[:3]]}")
        
        return products
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Test the BM25 retriever
if __name__ == "__main__":
    retriever = BM25Retriever()
    
    print("=" * 80)
    print("TESTING BM25 RETRIEVER")
    print("=" * 80)
    
    test_queries = [
        "I like bose for audio devices, suggest me good products from other brands",
        "headphones similar to sony but not sony",
        "laptops like macbook but cheaper",
        "wireless earbuds alternatives to beats",
        "gaming monitors not from asus"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"{'='*80}")
        
        results = retriever.search_bm25(query, limit=5)
        
        for i, product in enumerate(results, 1):
            print(f"\n{i}. {product['title'][:70]}")
            print(f"   Store: {product['store']}")
            print(f"   Price: ${product['price']:.2f} | Rating: {product['rating']:.1f}★ ({product['num_reviews']:,} reviews)")
            print(f"   BM25 Score: {product['bm25_score']:.3f}")
    
    retriever.close()

