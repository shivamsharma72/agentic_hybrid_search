"""
Query-Aware Similarity Search
Finds similar products while keeping user's original intent in mind
"""

import numpy as np
from typing import List, Dict, Optional


class QueryAwareSimilarity:
    """
    Combines user's original query with selected product to find better matches
    """
    
    @staticmethod
    def create_hybrid_vector(
        original_query_emb: List[float],
        selected_product_emb: List[float],
        selected_reviews_emb: Optional[List[float]] = None,
        weights: Dict[str, float] = None
    ) -> List[float]:
        """
        Create a hybrid query vector that combines:
        - User's original search intent
        - Selected product's characteristics
        - Selected product's review sentiment (optional)
        
        Args:
            original_query_emb: User's original query embedding
            selected_product_emb: Selected product's embedding
            selected_reviews_emb: Average review embedding for selected product
            weights: Custom weights {query, product, reviews}
            
        Returns:
            Hybrid embedding vector
        """
        
        # Default weights
        if weights is None:
            if selected_reviews_emb is not None:
                weights = {
                    "query": 0.3,      # Keep user intent
                    "product": 0.4,    # Product similarity
                    "reviews": 0.3     # Review similarity
                }
            else:
                weights = {
                    "query": 0.4,
                    "product": 0.6,
                    "reviews": 0.0
                }
        
        # Convert to numpy arrays
        query_vec = np.array(original_query_emb)
        product_vec = np.array(selected_product_emb)
        
        # Combine vectors
        hybrid = (
            weights["query"] * query_vec +
            weights["product"] * product_vec
        )
        
        if selected_reviews_emb is not None and weights.get("reviews", 0) > 0:
            review_vec = np.array(selected_reviews_emb)
            hybrid += weights["reviews"] * review_vec
        
        # Normalize to unit vector
        hybrid = hybrid / np.linalg.norm(hybrid)
        
        return hybrid.tolist()
    
    @staticmethod
    def explain_similarity(
        original_query: str,
        selected_product_title: str,
        similar_product_title: str,
        scores: Dict[str, float]
    ) -> str:
        """
        Generate a human-readable explanation of why a product is similar
        
        Args:
            original_query: User's original search
            selected_product_title: Product user selected
            similar_product_title: Similar product found
            scores: Similarity breakdown
            
        Returns:
            Explanation string
        """
        
        explanations = []
        
        # Query match
        if scores.get("query_similarity", 0) > 0.7:
            explanations.append(f"matches your search for '{original_query}'")
        
        # Product match
        if scores.get("product_similarity", 0) > 0.7:
            explanations.append(f"similar specs to {selected_product_title}")
        
        # Review match
        if scores.get("review_similarity", 0) > 0.7:
            explanations.append("users describe it similarly")
        
        if not explanations:
            return "semantically related"
        
        return " and ".join(explanations)


def create_query_aware_search_query(
    hybrid_embedding: List[float],
    category: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    limit: int = 10
) -> str:
    """
    Generate SQL query for query-aware similarity search
    
    Args:
        hybrid_embedding: Combined query/product/review embedding
        category: Category filter
        price_min: Minimum price
        price_max: Maximum price
        limit: Number of results
        
    Returns:
        SQL query string with placeholders
    """
    
    where_clauses = ["p.blair_embedding IS NOT NULL", "p.price IS NOT NULL"]
    
    if category:
        where_clauses.append("p.main_category ILIKE %(category)s")
    
    if price_min is not None:
        where_clauses.append("p.price >= %(price_min)s")
    
    if price_max is not None:
        where_clauses.append("p.price <= %(price_max)s")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
        SELECT 
            p.parent_asin,
            p.title,
            p.price,
            p.average_rating,
            p.rating_number,
            p.main_category,
            p.images,
            1 - (p.blair_embedding <=> %(hybrid_embedding)s::vector) as combined_similarity
        FROM products_backup p
        WHERE {where_clause}
        ORDER BY p.blair_embedding <=> %(hybrid_embedding)s::vector
        LIMIT %(limit)s;
    """
    
    return query


# Example usage
if __name__ == "__main__":
    import random
    
    # Simulate embeddings (768-dim)
    query_emb = [random.random() for _ in range(768)]
    product_emb = [random.random() for _ in range(768)]
    review_emb = [random.random() for _ in range(768)]
    
    # Create hybrid vector
    hybrid = QueryAwareSimilarity.create_hybrid_vector(
        query_emb,
        product_emb,
        review_emb
    )
    
    print(f"Hybrid vector created: {len(hybrid)} dimensions")
    print(f"Norm: {np.linalg.norm(hybrid):.4f} (should be ~1.0)")
    
    # Test explanation
    explanation = QueryAwareSimilarity.explain_similarity(
        "gaming laptop under $1000",
        "Dell XPS 13",
        "HP Pavilion Gaming",
        {
            "query_similarity": 0.85,
            "product_similarity": 0.72,
            "review_similarity": 0.68
        }
    )
    
    print(f"\nExplanation: {explanation}")

