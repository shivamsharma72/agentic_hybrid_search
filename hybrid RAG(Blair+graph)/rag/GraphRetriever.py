from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv("../graph_db/graph_db_env/.env")

class GraphRetriever:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        print(f"✅ Connected to Neo4j at {self.uri}")

    def close(self):
        self.driver.close()

    def get_candidate_asins(self, filters: Dict[str, str]) -> List[str]:
        """
        Step 1: Get candidate ASINs based on hard constraints.
        filters: {'ram': '16GB', 'price_category': 'Cheap', ...}
        """
        if not filters:
            return []

        query_parts = ["MATCH (p:Product)"]
        
        # Add matches for each filter
        # Note: This assumes specific relationship names and node labels based on schema
        # We map common user terms to graph schema
        
        if 'ram' in filters:
            query_parts.append(f"MATCH (p)-[:HAS_RAM]->(:RAMSize {{value: '{filters['ram']}'}})")
        
        if 'price_category' in filters:
            query_parts.append(f"MATCH (p)-[:HAS_PRICE_CATEGORY]->(:PriceCategory {{name: '{filters['price_category']}'}})")
            
        if 'storage_type' in filters:
             query_parts.append(f"MATCH (p)-[:HAS_TYPE]->(:StorageType {{name: '{filters['storage_type']}'}})")

        if 'color' in filters:
             query_parts.append(f"MATCH (p)-[:IS_OF_COLOR]->(:Color {{name: '{filters['color']}'}})")

        if 'os' in filters:
             query_parts.append(f"MATCH (p)-[:HAS_OPERATING_SYSTEM]->(:OS {{name: '{filters['os']}'}})")

        if 'storage_size' in filters:
             query_parts.append(f"MATCH (p)-[:HAS_STORAGE_SIZE_OF]->(:StorageSize {{value: '{filters['storage_size']}'}})")

        if 'weight' in filters:
             query_parts.append(f"MATCH (p)-[:LAPTOP_IS_WEIGHT_CATEGORY]->(:WeightCategory {{name: '{filters['weight']}'}})")

        query_parts.append("RETURN p.parent_asin as asin")
        
        query = "\n".join(query_parts)
        # print(f"🔍 Graph Query:\n{query}")
        
        with self.driver.session() as session:
            result = session.run(query)
            asins = [record["asin"] for record in result]
            
        return asins

    def enrich_product_sentiment(self, asin: str) -> Dict[str, str]:
        """
        Step 3: Enrich results with "Sentiment Scores" from the graph.
        Returns a dictionary of feature -> sentiment summary.
        """
        query = """
        MATCH (p:Product {parent_asin: $asin})<-[:REVIEWED]-(u:User)-[:WROTE]->(r:Review)-[:USER_SAID]->(f:Feature)-[:HAS_SENTIMENT]->(s:Sentiment)
        RETURN f.name as feature, s.value as sentiment, count(*) as count
        ORDER BY count DESC
        LIMIT 10
        """
        
        with self.driver.session() as session:
            result = session.run(query, asin=asin)
            
            # Aggregate sentiment counts
            feature_stats = {}
            for record in result:
                feature = record["feature"]
                sentiment = record["sentiment"]
                count = record["count"]
                
                if feature not in feature_stats:
                    feature_stats[feature] = {"Total": 0}
                
                if sentiment not in feature_stats[feature]:
                    feature_stats[feature][sentiment] = 0
                
                feature_stats[feature][sentiment] += count
                feature_stats[feature]["Total"] += count
        
        # Format output
        enrichment = {}
        for feature, stats in feature_stats.items():
            total = stats["Total"]
            if total > 0:
                # Calculate positive percentage if "Positive" exists, otherwise 0
                pos_count = stats.get("Positive", 0)
                pos_pct = (pos_count / total) * 100
                enrichment[feature] = f"{pos_pct:.0f}% Positive ({total} mentions)"
                
        return enrichment
