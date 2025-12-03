#!/usr/bin/env python3
"""
C4 Dataset Evaluation Script
Evaluates retrieval performance using C4 dataset queries
Checks if correct product appears in top 10 results
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from tqdm import tqdm
import psycopg2

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'CODE', 'backend'))

from rag_chatbot.embedding_model import EmbeddingModel
from rag_chatbot.retriever import EnhancedHybridRetriever
from rag_chatbot import config

class C4Evaluator:
    """Evaluate retrieval performance using C4 dataset"""
    
    def __init__(self):
        """Initialize evaluator with embedding model and retriever"""
        print("🔧 Initializing evaluation components...")
        self.embedding_model = EmbeddingModel()
        # Enable reranker for better performance
        # Pass embedding_model to retriever to avoid reloading it
        self.retriever = EnhancedHybridRetriever(
            db_name=config.DB_NAME, 
            use_reranker=True,
            embedding_model=self.embedding_model
        )
        print("✅ Components initialized\n")
    
    def load_c4_dataset(self, dataset_path: str) -> pd.DataFrame:
        """
        Load C4 dataset from file
        
        Expected format: CSV or JSON with columns:
        - query: Complex query text
        - product_id: Expected product ASIN
        - (optional) category, price_range, etc.
        
        Args:
            dataset_path: Path to C4 dataset file
            
        Returns:
            DataFrame with queries and product IDs
        """
        print(f"📂 Loading C4 dataset from {dataset_path}...")
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
        
        # Try different formats
        if dataset_path.endswith('.json'):
            df = pd.read_json(dataset_path)
        elif dataset_path.endswith('.csv'):
            df = pd.read_csv(dataset_path)
        else:
            raise ValueError(f"Unsupported file format: {dataset_path}")
        
        # Validate required columns - handle both 'product_id' and 'asin'
        if 'product_id' not in df.columns and 'asin' not in df.columns:
            raise ValueError("Missing required column: need either 'product_id' or 'asin'")
        
        if 'query' not in df.columns:
            raise ValueError("Missing required column: 'query'")
        
        # Normalize column name: rename 'asin' to 'product_id' for consistency
        if 'asin' in df.columns and 'product_id' not in df.columns:
            df = df.rename(columns={'asin': 'product_id'})
        
        print(f"✅ Loaded {len(df)} queries from dataset")
        return df
    
    def filter_to_database_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter dataset to only include product IDs that exist in database
        
        Args:
            df: DataFrame with queries and product_ids
            
        Returns:
            Filtered DataFrame
        """
        print("\n🔍 Filtering to products in database...")
        
        # Get all product IDs from database
        import psycopg2
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        cur = conn.cursor()
        cur.execute(f"SELECT parent_asin FROM {config.PRODUCTS_TABLE};")
        db_products = set(row[0] for row in cur.fetchall())
        cur.close()
        conn.close()
        
        print(f"   Database has {len(db_products)} products")
        
        # Filter dataset
        initial_count = len(df)
        df_filtered = df[df['product_id'].isin(db_products)].copy()
        filtered_count = len(df_filtered)
        
        print(f"   Filtered: {initial_count} → {filtered_count} queries")
        print(f"   Removed: {initial_count - filtered_count} queries (products not in DB)")
        
        return df_filtered
    
    def evaluate_query(self, query: str, expected_product_id: str, top_k: int = 10) -> Dict:
        """
        Evaluate a single query
        
        Args:
            query: Query text
            expected_product_id: Expected product ASIN
            top_k: Number of top results to check
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode_query(query)
        
        # Search for products (with reranker if enabled)
        products = self.retriever.search_unified(
            query_embedding=query_embedding,
            query_text=query,  # Pass query text for reranker
            strategy="balanced",
            top_products=top_k * 2,  # Get more candidates for reranker
            top_reviews=50
        )
        
        # Extract product ASINs from results
        retrieved_asins = [p.asin for p in products[:top_k]]
        
        # Check if expected product is in results
        rank = None
        if expected_product_id in retrieved_asins:
            rank = retrieved_asins.index(expected_product_id) + 1  # 1-indexed
        
        # Calculate metrics
        recall_at_k = 1.0 if rank is not None else 0.0
        mrr = 1.0 / rank if rank is not None else 0.0
        
        return {
            'query': query,
            'expected_product_id': expected_product_id,
            'rank': rank,
            'recall_at_k': recall_at_k,
            'mrr': mrr,
            'retrieved_asins': retrieved_asins[:top_k]
        }
    
    def evaluate_dataset(self, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        """
        Evaluate entire dataset
        
        Args:
            df: DataFrame with queries and product_ids
            top_k: Number of top results to check
            
        Returns:
            DataFrame with evaluation results
        """
        print(f"\n📊 Evaluating {len(df)} queries (checking top {top_k} results)...")
        print("=" * 80)
        
        results = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating queries"):
            query = row['query']
            product_id = row['product_id']
            
            try:
                result = self.evaluate_query(query, product_id, top_k=top_k)
                results.append(result)
            except Exception as e:
                print(f"\n⚠️  Error evaluating query '{query[:50]}...': {e}")
                results.append({
                    'query': query,
                    'expected_product_id': product_id,
                    'rank': None,
                    'recall_at_k': 0.0,
                    'mrr': 0.0,
                    'retrieved_asins': [],
                    'error': str(e)
                })
        
        results_df = pd.DataFrame(results)
        return results_df
    
    def calculate_metrics(self, results_df: pd.DataFrame, top_k: int = 10) -> Dict:
        """
        Calculate aggregate evaluation metrics
        
        Args:
            results_df: DataFrame with evaluation results
            top_k: Top K value used
            
        Returns:
            Dictionary with aggregate metrics
        """
        print("\n" + "=" * 80)
        print("📈 AGGREGATE METRICS")
        print("=" * 80)
        
        total_queries = len(results_df)
        
        # Recall@K
        recall_at_k = results_df['recall_at_k'].mean()
        
        # MRR (Mean Reciprocal Rank)
        mrr = results_df['mrr'].mean()
        
        # Rank distribution
        valid_ranks = results_df[results_df['rank'].notna()]['rank']
        rank_stats = {
            'mean': valid_ranks.mean() if len(valid_ranks) > 0 else None,
            'median': valid_ranks.median() if len(valid_ranks) > 0 else None,
            'min': valid_ranks.min() if len(valid_ranks) > 0 else None,
            'max': valid_ranks.max() if len(valid_ranks) > 0 else None,
        }
        
        # Rank distribution (how many at each rank)
        rank_distribution = {}
        for rank in range(1, top_k + 1):
            count = (results_df['rank'] == rank).sum()
            rank_distribution[f'rank_{rank}'] = count
        
        # Not found count
        not_found = (results_df['rank'].isna()).sum()
        
        metrics = {
            'total_queries': total_queries,
            f'recall_at_{top_k}': recall_at_k,
            'mrr': mrr,
            'not_found': not_found,
            'found': total_queries - not_found,
            'rank_statistics': rank_stats,
            'rank_distribution': rank_distribution
        }
        
        # Print metrics
        print(f"\n📊 Total Queries: {total_queries}")
        print(f"✅ Found in top {top_k}: {total_queries - not_found} ({100*(total_queries - not_found)/total_queries:.1f}%)")
        print(f"❌ Not found: {not_found} ({100*not_found/total_queries:.1f}%)")
        print(f"\n🎯 Recall@{top_k}: {recall_at_k:.4f} ({recall_at_k*100:.2f}%)")
        print(f"📈 MRR (Mean Reciprocal Rank): {mrr:.4f}")
        
        if rank_stats['mean']:
            print(f"\n📊 Rank Statistics:")
            print(f"   Mean Rank: {rank_stats['mean']:.2f}")
            print(f"   Median Rank: {rank_stats['median']:.2f}")
            print(f"   Best Rank: {rank_stats['min']}")
            print(f"   Worst Rank: {rank_stats['max']}")
        
        print(f"\n📋 Rank Distribution:")
        for rank in range(1, min(11, top_k + 1)):
            count = rank_distribution.get(f'rank_{rank}', 0)
            pct = 100 * count / total_queries if total_queries > 0 else 0
            print(f"   Rank {rank}: {count} queries ({pct:.1f}%)")
        
        return metrics
    
    def save_results(self, results_df: pd.DataFrame, metrics: Dict, output_dir: str = "evaluation/results"):
        """
        Save evaluation results to files
        
        Args:
            results_df: DataFrame with evaluation results
            metrics: Dictionary with aggregate metrics
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Save detailed results
        results_path = os.path.join(output_dir, "c4_evaluation_results.csv")
        results_df.to_csv(results_path, index=False)
        print(f"\n💾 Saved detailed results to: {results_path}")
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        metrics_serializable = convert_numpy_types(metrics)
        
        # Save metrics
        metrics_path = os.path.join(output_dir, "c4_evaluation_metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics_serializable, f, indent=2)
        print(f"💾 Saved metrics to: {metrics_path}")
    
    def close(self):
        """Clean up resources"""
        if self.retriever:
            self.retriever.close()


def main():
    """Main evaluation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate retrieval using C4 dataset")
    parser.add_argument('--dataset', type=str, required=True,
                       help='Path to C4 dataset file (CSV or JSON)')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of top results to check (default: 10)')
    parser.add_argument('--output-dir', type=str, default='evaluation/results',
                       help='Output directory for results (default: evaluation/results)')
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = C4Evaluator()
    
    try:
        # Load dataset
        df = evaluator.load_c4_dataset(args.dataset)
        
        # Filter to database products
        df_filtered = evaluator.filter_to_database_products(df)
        
        if len(df_filtered) == 0:
            print("\n❌ No queries remaining after filtering to database products!")
            print("   Please check that product IDs in dataset match database ASINs")
            return
        
        # Evaluate
        results_df = evaluator.evaluate_dataset(df_filtered, top_k=args.top_k)
        
        # Calculate metrics
        metrics = evaluator.calculate_metrics(results_df, top_k=args.top_k)
        
        # Save results
        evaluator.save_results(results_df, metrics, output_dir=args.output_dir)
        
        print("\n" + "=" * 80)
        print("✅ EVALUATION COMPLETE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        evaluator.close()


if __name__ == "__main__":
    main()

