"""
BLAIR-RoBERTa Embedding Model for Query Embeddings

IMPORTANT: This uses CLS pooling (first token) to match the product embeddings
that were generated using the same method. Do NOT change to mean pooling unless
you re-generate all 348K product embeddings.
"""

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List, Union

class EmbeddingModel:
    """Wrapper for BLAIR-RoBERTa embedding model"""
    
    def __init__(self, model_name: str = "hyp1231/blair-roberta-base", device: str = None):
        """
        Initialize the embedding model
        
        Args:
            model_name: HuggingFace model name
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto)
        """
        print(f"📦 Loading embedding model: {model_name}")
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        
        self.device = device
        print(f"   Device: {device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()
        
        print(f"✅ Model loaded successfully")
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Encode texts into embeddings
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings (shape: [num_texts, 768])
        """
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        embeddings = []
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Tokenize
                encoded = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors='pt'
                ).to(self.device)
                
                # Get embeddings
                outputs = self.model(**encoded)
                
                # CLS pooling (match product embedding generation)
                # Use first token [CLS] instead of mean pooling
                batch_embeddings = outputs.last_hidden_state[:, 0, :]
                
                embeddings.append(batch_embeddings.cpu().numpy())
        
        # Concatenate all batches
        embeddings = np.concatenate(embeddings, axis=0)
        
        # Return single embedding if input was single text
        if single_input:
            return embeddings[0]
        
        return embeddings
    
    def encode_query(self, query: str) -> List[float]:
        """
        Encode a single query into embedding (returns list for PostgreSQL)
        
        Args:
            query: Query text
            
        Returns:
            List of floats (768-dim)
        """
        embedding = self.encode(query)
        return embedding.tolist()


# Singleton instance (lazy loading)
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    """Get or create the embedding model singleton"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model

