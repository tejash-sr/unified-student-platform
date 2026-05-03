"""
Embeddings and vector similarity utilities for RAG and recommendations.
Powers semantic search, course matching, and knowledge retrieval.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing embeddings.
    Uses sentence-transformers for semantic understanding.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Models:
        - all-MiniLM-L6-v2: Fast, 384 dims, good for quick retrieval
        - all-mpnet-base-v2: Better quality, 768 dims
        - all-distilroberta-v1: Balanced, 768 dims
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ Loaded embedding model: {model_name} ({self.embedding_dim}D)")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        if not self.model:
            raise RuntimeError("Embedding model not initialized")
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    def encode_single(self, text: str) -> List[float]:
        """Encode single text."""
        return self.encode([text])[0]
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts (0-1)."""
        emb1 = self.encode_single(text1)
        emb2 = self.encode_single(text2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def batch_similarity(self, query: str, documents: List[str]) -> List[float]:
        """Calculate similarity of query to multiple documents."""
        query_emb = self.encode_single(query)
        doc_embs = self.encode(documents)
        
        similarities = []
        for doc_emb in doc_embs:
            sim = float(np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)))
            similarities.append(sim)
        
        return similarities


class ChromaVectorDB:
    """
    Vector database service using ChromaDB.
    Manages knowledge base for semantic search and RAG.
    """
    
    def __init__(self, collection_name: str = "student_knowledge_base", persist_dir: str = "./chroma_data"):
        """Initialize ChromaDB client and collection."""
        try:
            settings = Settings(
                chroma_db_impl="duckdb",
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            )
            self.client = chromadb.Client(settings)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✅ Initialized ChromaDB collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to knowledge base."""
        if not self.collection:
            raise RuntimeError("ChromaDB collection not initialized")
        
        if not ids:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"✅ Added {len(documents)} documents to ChromaDB")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where_filter: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base using semantic similarity.
        
        Returns: List of matched documents with scores
        """
        if not self.collection:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["embeddings", "metadatas", "documents", "distances"]
            )
            
            # Format results
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []
            
            # Convert distances to similarity scores (1 - distance for cosine)
            formatted_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                similarity = 1 - dist  # Cosine distance to similarity
                formatted_results.append({
                    "document": doc,
                    "metadata": meta,
                    "similarity_score": float(similarity),
                })
            
            return sorted(formatted_results, key=lambda x: x["similarity_score"], reverse=True)
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def delete(self, ids: List[str]) -> None:
        """Delete documents from collection."""
        if self.collection:
            self.collection.delete(ids=ids)
    
    def clear(self) -> None:
        """Clear all documents from collection."""
        if self.collection:
            try:
                # Get all IDs and delete
                data = self.collection.get()
                if data["ids"]:
                    self.collection.delete(ids=data["ids"])
                logger.info("✅ Cleared ChromaDB collection")
            except Exception as e:
                logger.warning(f"Could not clear collection: {e}")


class SemanticMatcher:
    """
    Semantic matching engine for recommendations.
    Matches users to courses/universities based on profile similarity.
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embeddings = embedding_service
    
    def create_user_profile_description(self, user_profile: Dict[str, Any]) -> str:
        """Generate semantic description of user profile."""
        
        parts = []
        
        if user_profile.get("preferred_fields"):
            parts.append(f"Interests: {', '.join(user_profile['preferred_fields'])}")
        
        if user_profile.get("current_cgpa"):
            parts.append(f"Academic Level: CGPA {user_profile['current_cgpa']}/4.0")
        
        if user_profile.get("work_experience_years"):
            parts.append(f"Experience: {user_profile['work_experience_years']} years")
        
        if user_profile.get("preferred_countries"):
            parts.append(f"Preferred Regions: {', '.join(user_profile['preferred_countries'])}")
        
        if user_profile.get("budget_range_max"):
            parts.append(f"Budget: up to {user_profile['budget_range_max']} INR")
        
        return ". ".join(parts) if parts else "Student seeking higher education"
    
    def match_courses(
        self,
        user_profile: Dict[str, Any],
        courses: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> List[Tuple[Dict, float]]:
        """
        Match user to courses using semantic similarity.
        
        Returns: List of (course, match_score) tuples
        """
        user_description = self.create_user_profile_description(user_profile)
        
        matches = []
        for course in courses:
            course_description = f"{course.get('name')} in {course.get('field')}: {course.get('description', '')}"
            
            similarity = self.embeddings.similarity(user_description, course_description)
            
            # Add bonus scoring for explicit preferences
            bonus = 0
            if course.get("field") in user_profile.get("preferred_fields", []):
                bonus += 0.15
            if course.get("country") in user_profile.get("preferred_countries", []):
                bonus += 0.10
            
            total_score = min(1.0, similarity + bonus)
            matches.append((course, total_score))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)[:top_k]


# Global instances (lazy loaded)
_embedding_service: Optional[EmbeddingService] = None
_vector_db: Optional[ChromaVectorDB] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_vector_db() -> ChromaVectorDB:
    """Get or create vector database."""
    global _vector_db
    if _vector_db is None:
        _vector_db = ChromaVectorDB()
    return _vector_db


# Convenience function for similarity
def semantic_similarity(text1: str, text2: str) -> float:
    """Quick semantic similarity calculation."""
    service = get_embedding_service()
    return service.similarity(text1, text2)
