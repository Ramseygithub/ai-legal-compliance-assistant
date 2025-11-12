import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from app.ai_client import AlibabaBailianClient
from app.storage import storage
import uuid

class VectorEmbeddingService:
    def __init__(self):
        self.ai_client = AlibabaBailianClient()
        
    def embed_text_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将文本片段转换为向量嵌入"""
        if not segments:
            return []
        
        texts = [segment["content"] for segment in segments]
        embeddings = self.ai_client.get_embeddings(texts)
        
        embedded_segments = []
        for i, segment in enumerate(segments):
            embedded_segment = segment.copy()
            embedded_segment["vector"] = embeddings[i]
            embedded_segment["vector_dim"] = len(embeddings[i])
            embedded_segments.append(embedded_segment)
        
        return embedded_segments
    
    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """计算两个向量的相似度"""
        if not vector1 or not vector2:
            return 0.0
        
        vec1 = np.array(vector1).reshape(1, -1)
        vec2 = np.array(vector2).reshape(1, -1)
        
        similarity = cosine_similarity(vec1, vec2)[0][0]
        return float(similarity)
    
    def find_similar_segments(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """查找与查询文本最相似的文档片段"""
        query_embedding = self.ai_client.get_embeddings([query_text])[0]
        
        all_segments = []
        vectors_data = storage.load_vectors()
        
        for doc_id, doc_vectors in vectors_data.items():
            if "segments" in doc_vectors:
                all_segments.extend(doc_vectors["segments"])
        
        if not all_segments:
            return []
        
        similarities = []
        for segment in all_segments:
            if "vector" in segment:
                similarity = self.calculate_similarity(query_embedding, segment["vector"])
                similarities.append((similarity, segment))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for similarity, segment in similarities[:top_k]:
            result = segment.copy()
            result["similarity_score"] = similarity
            results.append(result)
        
        return results
    
    def create_regulation_index(self, doc_id: str, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """为法规文档创建向量索引"""
        embedded_segments = self.embed_text_segments(segments)
        
        index_data = {
            "document_id": doc_id,
            "segments": embedded_segments,
            "total_segments": len(embedded_segments),
            "created_at": segments[0]["created_at"] if segments else None,
            "index_id": str(uuid.uuid4())
        }
        
        vectors_data = storage.load_vectors()
        vectors_data[doc_id] = index_data
        storage.save_vectors(vectors_data)
        
        return index_data
    
    def search_regulations(self, query: str, filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """在法规库中搜索相关内容"""
        similar_segments = self.find_similar_segments(query, top_k * 2)
        
        if filters:
            filtered_segments = []
            for segment in similar_segments:
                include = True
                
                if "min_similarity" in filters and segment["similarity_score"] < filters["min_similarity"]:
                    include = False
                
                if "keywords" in filters:
                    keywords = filters["keywords"]
                    if not any(keyword in segment["content"] for keyword in keywords):
                        include = False
                
                if include:
                    filtered_segments.append(segment)
            
            similar_segments = filtered_segments
        
        return similar_segments[:top_k]
    
    def get_vector_statistics(self) -> Dict[str, Any]:
        """获取向量库统计信息"""
        vectors_data = storage.load_vectors()
        
        total_documents = len(vectors_data)
        total_segments = sum(len(doc_data.get("segments", [])) for doc_data in vectors_data.values())
        
        vector_dims = []
        for doc_data in vectors_data.values():
            segments = doc_data.get("segments", [])
            for segment in segments:
                if "vector" in segment:
                    vector_dims.append(segment.get("vector_dim", 0))
        
        avg_vector_dim = np.mean(vector_dims) if vector_dims else 0
        
        return {
            "total_documents": total_documents,
            "total_segments": total_segments,
            "average_vector_dimension": float(avg_vector_dim),
            "vector_count": len(vector_dims)
        }