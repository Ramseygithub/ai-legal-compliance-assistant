from typing import List, Dict, Any, Optional
from app.vector_service import VectorEmbeddingService
from app.ai_client import AlibabaBailianClient
from app.storage import storage
from app.knowledge_graph import KnowledgeGraphBuilder
import json

class RAGService:
    def __init__(self):
        self.vector_service = VectorEmbeddingService()
        self.ai_client = AlibabaBailianClient()
        self.kg_builder = KnowledgeGraphBuilder()
    
    def retrieve_relevant_documents(self, query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Retrieve document segments related to the query"""
        similar_segments = self.vector_service.find_similar_segments(query, top_k * 2)
        
        filtered_segments = [
            segment for segment in similar_segments 
            if segment.get("similarity_score", 0) >= similarity_threshold
        ]
        
        return filtered_segments[:top_k]
    
    def enhance_context_with_kg(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance context using knowledge graph"""
        enhanced_docs = retrieved_docs.copy()
        
        try:
            kg_results = self.kg_builder.query_knowledge_graph(query)
            
            if kg_results["nodes"]:
                kg_context = {
                    "id": "kg_context",
                    "content": self._format_kg_context(kg_results),
                    "similarity_score": 0.9,
                    "source": "knowledge_graph",
                    "type": "knowledge_graph"
                }
                enhanced_docs.insert(0, kg_context)
        
        except Exception as e:
            print(f"Knowledge graph enhancement failed: {e}")
        
        return enhanced_docs
    
    def _format_kg_context(self, kg_results: Dict[str, Any]) -> str:
        """Format knowledge graph context"""
        context_parts = ["Related legal entities and relationships:\n"]
        
        for node in kg_results["nodes"][:5]:
            context_parts.append(f"- {node['label']} ({node['type']})")
        
        if kg_results["edges"]:
            context_parts.append("\nRelated legal relationships:")
            for edge in kg_results["edges"][:3]:
                source_node = next((n for n in kg_results["nodes"] if n["id"] == edge["source"]), {})
                target_node = next((n for n in kg_results["nodes"] if n["id"] == edge["target"]), {})
                
                if source_node and target_node:
                    context_parts.append(
                        f"- {source_node.get('label', 'Unknown')} {edge['relation']} {target_node.get('label', 'Unknown')}"
                    )
        
        return "\n".join(context_parts)
    
    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer based on retrieved documents"""
        context_text = self._build_context_text(context_docs)
        
        prompt = f"""As a legal expert, please answer the question based on the following legal documents. Ensure your answer is accurate, complete, and cites specific articles or documents.

Related Legal Documents:
{context_text}

Question: {query}

Please answer in the following format:
1. Direct answer to the question
2. Specific legal articles or regulations cited
3. Related suggestions or considerations

Answer:"""
        
        try:
            answer = self.ai_client.generate_text(prompt, max_tokens=1500)
            
            confidence = self._calculate_answer_confidence(context_docs, query)
            
            sources = []
            for doc in context_docs[:3]:
                if doc.get("source") != "knowledge_graph":
                    sources.append({
                        "content": doc["content"][:200] + "...",
                        "similarity_score": doc.get("similarity_score", 0),
                        "document_id": doc.get("document_id", "unknown")
                    })
            
            return {
                "answer": answer,
                "confidence": confidence,
                "sources": sources,
                "context_used": len(context_docs)
            }
        
        except Exception as e:
            return {
                "answer": f"Sorry, an error occurred while generating the answer: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "context_used": 0
            }
    
    def _build_context_text(self, context_docs: List[Dict[str, Any]], max_length: int = 3000) -> str:
        """Build context text"""
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(context_docs, 1):
            doc_text = f"[Document {i}] {doc['content']}"
            
            if current_length + len(doc_text) > max_length:
                remaining_length = max_length - current_length
                if remaining_length > 100:
                    doc_text = doc_text[:remaining_length] + "..."
                    context_parts.append(doc_text)
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "\n\n".join(context_parts)
    
    def _calculate_answer_confidence(self, context_docs: List[Dict[str, Any]], query: str) -> float:
        """Calculate answer confidence"""
        if not context_docs:
            return 0.0
        
        avg_similarity = sum(doc.get("similarity_score", 0) for doc in context_docs) / len(context_docs)
        
        context_length_factor = min(len(context_docs) / 5.0, 1.0)
        
        query_coverage = 0.8 if len(query) > 10 else 0.5
        
        confidence = (avg_similarity * 0.5 + context_length_factor * 0.3 + query_coverage * 0.2)
        
        return round(confidence, 2)
    
    def ask_question(self, question: str, top_k: int = 5, use_kg: bool = True) -> Dict[str, Any]:
        """Complete Q&A workflow"""
        try:
            retrieved_docs = self.retrieve_relevant_documents(question, top_k)
            
            if not retrieved_docs:
                return {
                    "answer": "Sorry, no relevant regulatory documents found to answer your question.",
                    "confidence": 0.0,
                    "sources": [],
                    "context_used": 0
                }
            
            if use_kg:
                enhanced_docs = self.enhance_context_with_kg(question, retrieved_docs)
            else:
                enhanced_docs = retrieved_docs
            
            result = self.generate_answer(question, enhanced_docs)
            result["query"] = question
            result["retrieval_count"] = len(retrieved_docs)
            
            return result
        
        except Exception as e:
            return {
                "answer": f"System error: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "context_used": 0,
                "error": str(e)
            }
    
    def batch_qa(self, questions: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Batch Q&A"""
        results = []
        
        for question in questions:
            result = self.ask_question(question, top_k)
            results.append(result)
        
        return results
    
    def suggest_related_questions(self, original_question: str, num_suggestions: int = 3) -> List[str]:
        """Suggest related questions based on original question"""
        retrieved_docs = self.retrieve_relevant_documents(original_question, 5)
        
        if not retrieved_docs:
            return []
        
        context_text = self._build_context_text(retrieved_docs, 1000)
        
        prompt = f"""Based on the following regulatory content and original question, suggest {num_suggestions} related legal questions:

Regulatory Content:
{context_text}

Original Question: {original_question}

Please generate {num_suggestions} related questions, one per line:"""
        
        try:
            response = self.ai_client.generate_text(prompt, max_tokens=500)
            
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and '?' in line or '？' in line:
                    line = line.lstrip('123456789. -')
                    suggestions.append(line)
            
            return suggestions[:num_suggestions]
        
        except:
            return []