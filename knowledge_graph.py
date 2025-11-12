import json
import re
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
from app.storage import storage
from app.ai_client import AlibabaBailianClient
import uuid

class KnowledgeGraphBuilder:
    def __init__(self):
        self.ai_client = AlibabaBailianClient()
        self.entity_types = {
            "legal_articles": "LEGAL_ARTICLE",
            "violations": "VIOLATION",
            "penalties": "PENALTY",
            "responsible_parties": "RESPONSIBLE_PARTY",
            "related_concepts": "CONCEPT"
        }
        self.use_local_extraction = False  # Flag to use local extraction when API fails
    
    def _local_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Local rule-based entity extraction as fallback"""
        entities = {
            "legal_articles": [],
            "violations": [],
            "penalties": [],
            "responsible_parties": [],
            "related_concepts": []
        }
        
        # Extract legal articles (e.g., Article 5, Section 2, ABC Law)
        import re
        article_patterns = [
            r'\b(?:Article|Section|Clause|Part|Chapter|Regulation)\s+\d+[a-zA-Z]?\b',
            r'\b[A-Z][A-Za-z]+\s+(?:Law|Act|Code|Regulation|Rule)\b',
            r'\b(?:Title|Subtitle)\s+[IVXLCDM]+\b',
            r'\bABC\s+Law\b'
        ]
        for pattern in article_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["legal_articles"].extend(matches)
        
        # Extract violations
        violation_keywords = [
            'violation', 'breach', 'infringement', 'non-compliance', 'illegal',
            'prohibited', 'unlawful', 'monopoly', 'discrimination', 'fraud',
            'price fixing', 'market manipulation', 'unfair competition'
        ]
        for keyword in violation_keywords:
            if keyword.lower() in text.lower():
                # Extract surrounding context
                pattern = r'(?:[\w\s]{0,20}' + re.escape(keyword) + r'[\w\s]{0,20})'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:2]:  # Limit to avoid too many
                    entities["violations"].append(match.strip())
        
        # Extract penalties
        penalty_patterns = [
            r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|thousand|billion))?',
            r'\b\d+\s*(?:years?|months?|days?)\s*(?:in\s*)?(?:prison|jail|imprisonment)',
            r'\b(?:fine|penalty|sanction|punishment)\s*(?:of|up\s*to)?\s*[\w\s]+',
            r'\b(?:suspension|revocation|termination)\s*of\s*(?:license|permit|authorization)'
        ]
        for pattern in penalty_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["penalties"].extend(matches)
        
        # Extract responsible parties
        party_patterns = [
            r'\b(?:supplier|wholesaler|retailer|distributor|manufacturer|company|corporation|business|entity)\b',
            r'\b(?:licensee|permit\s*holder|operator|owner|manager)\b'
        ]
        for pattern in party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Deduplicate while preserving order
            seen = set()
            for match in matches:
                if match.lower() not in seen:
                    entities["responsible_parties"].append(match)
                    seen.add(match.lower())
        
        # Extract related concepts
        concept_keywords = [
            'compliance', 'regulation', 'pricing', 'market', 'competition',
            'trade', 'commerce', 'consumer protection', 'antitrust',
            'three-tier system', 'posted price', 'inducement'
        ]
        for keyword in concept_keywords:
            if keyword.lower() in text.lower():
                entities["related_concepts"].append(keyword)
        
        # Remove duplicates while preserving order
        for entity_type in entities:
            seen = set()
            unique = []
            for item in entities[entity_type]:
                item_lower = item.lower() if item else ""
                if item and item_lower not in seen:
                    unique.append(item)
                    seen.add(item_lower)
            entities[entity_type] = unique[:5]  # Limit to 5 per type
        
        return entities
    
    def extract_entities_from_document(self, doc_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities from document"""
        segments = storage.load_segments(doc_id)
        document_data = storage.load_document(doc_id)
        
        if not segments:
            return {}
        
        all_entities = {entity_type: [] for entity_type in self.entity_types.keys()}
        
        for segment in segments:
            # Try AI extraction first
            entities = self.ai_client.extract_legal_entities(segment["content"])
            
            # Check if AI extraction failed (returns empty entities)
            if not any(entities.values()):
                # Use local extraction as fallback
                print(f"Using local entity extraction for segment {segment['id']}")
                entities = self._local_entity_extraction(segment["content"])
            
            for entity_type, entity_list in entities.items():
                if entity_type in all_entities:
                    for entity_text in entity_list:
                        entity_obj = {
                            "id": str(uuid.uuid4()),
                            "text": entity_text,
                            "type": self.entity_types.get(entity_type, "UNKNOWN"),
                            "document_id": doc_id,
                            "segment_id": segment["id"],
                            "confidence": 0.8 if any(entities.values()) else 0.6,  # Lower confidence for local extraction
                            "source": segment["content"][:200] + "..."
                        }
                        all_entities[entity_type].append(entity_obj)
        
        return all_entities
    
    def find_relationships(self, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify relationships between entities"""
        relationships = []
        
        for entity_type1, entity_list1 in entities.items():
            for entity1 in entity_list1:
                for entity_type2, entity_list2 in entities.items():
                    if entity_type1 != entity_type2:
                        for entity2 in entity_list2:
                            if entity1["segment_id"] == entity2["segment_id"]:
                                relation_type = self._determine_relation_type(entity_type1, entity_type2)
                                if relation_type:
                                    relationships.append({
                                        "id": str(uuid.uuid4()),
                                        "source": entity1["id"],
                                        "target": entity2["id"],
                                        "relation": relation_type,
                                        "confidence": 0.7,
                                        "evidence": entity1["source"]
                                    })
        
        return relationships
    
    def _determine_relation_type(self, type1: str, type2: str) -> str:
        """Determine relationship type between two entity types"""
        relation_map = {
            ("legal_articles", "violations"): "regulates",
            ("violations", "penalties"): "leads_to",
            ("legal_articles", "penalties"): "specifies_penalty",
            ("responsible_parties", "violations"): "commits",
            ("related_concepts", "legal_articles"): "involves",
            ("related_concepts", "violations"): "defines"
        }
        
        return relation_map.get((type1, type2), "")
    
    def build_knowledge_graph(self, doc_ids: List[str] = None) -> Dict[str, Any]:
        """Build knowledge graph"""
        if doc_ids is None:
            doc_ids = storage.list_documents()
        
        all_nodes = []
        all_edges = []
        entity_map = {}
        
        for doc_id in doc_ids:
            entities = self.extract_entities_from_document(doc_id)
            
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    node = {
                        "id": entity["id"],
                        "label": entity["text"],
                        "type": entity["type"],
                        "properties": {
                            "document_id": entity["document_id"],
                            "confidence": entity["confidence"],
                            "source": entity["source"]
                        }
                    }
                    all_nodes.append(node)
                    entity_map[entity["id"]] = entity
            
            relationships = self.find_relationships(entities)
            all_edges.extend(relationships)
        
        self._merge_similar_entities(all_nodes, all_edges)
        
        graph_data = {
            "nodes": all_nodes,
            "edges": all_edges,
            "metadata": {
                "total_nodes": len(all_nodes),
                "total_edges": len(all_edges),
                "document_count": len(doc_ids),
                "created_at": datetime.now().isoformat()
            }
        }
        
        storage.save_knowledge_graph(graph_data)
        return graph_data
    
    def _merge_similar_entities(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
        """Merge similar entities"""
        similar_groups = []
        processed = set()
        
        for i, node1 in enumerate(nodes):
            if node1["id"] in processed:
                continue
            
            group = [node1]
            for j, node2 in enumerate(nodes[i+1:], i+1):
                if node2["id"] in processed:
                    continue
                
                if (node1["type"] == node2["type"] and 
                    self._is_similar_text(node1["label"], node2["label"])):
                    group.append(node2)
                    processed.add(node2["id"])
            
            if len(group) > 1:
                similar_groups.append(group)
            processed.add(node1["id"])
        
        for group in similar_groups:
            main_node = group[0]
            merge_ids = [node["id"] for node in group[1:]]
            
            for edge in edges:
                if edge["source"] in merge_ids:
                    edge["source"] = main_node["id"]
                if edge["target"] in merge_ids:
                    edge["target"] = main_node["id"]
            
            for node_to_remove in group[1:]:
                if node_to_remove in nodes:
                    nodes.remove(node_to_remove)
    
    def _is_similar_text(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """Determine if two texts are similar"""
        if text1 == text2:
            return True
        
        if len(text1) < 3 or len(text2) < 3:
            return False
        
        common_chars = sum(1 for a, b in zip(text1, text2) if a == b)
        max_len = max(len(text1), len(text2))
        
        return (common_chars / max_len) >= threshold
    
    def query_knowledge_graph(self, entity_name: str, relation_type: str = None) -> Dict[str, Any]:
        """Query knowledge graph"""
        graph_data = storage.load_knowledge_graph()
        
        if not graph_data or "nodes" not in graph_data:
            return {"nodes": [], "edges": [], "message": "Knowledge graph is empty"}
        
        matching_nodes = []
        related_edges = []
        related_node_ids = set()
        
        for node in graph_data["nodes"]:
            if entity_name.lower() in node["label"].lower():
                matching_nodes.append(node)
                related_node_ids.add(node["id"])
        
        for edge in graph_data["edges"]:
            if (edge["source"] in related_node_ids or edge["target"] in related_node_ids):
                if relation_type is None or edge["relation"] == relation_type:
                    related_edges.append(edge)
                    related_node_ids.add(edge["source"])
                    related_node_ids.add(edge["target"])
        
        result_nodes = [node for node in graph_data["nodes"] if node["id"] in related_node_ids]
        
        return {
            "nodes": result_nodes,
            "edges": related_edges,
            "query_info": {
                "entity_name": entity_name,
                "relation_type": relation_type,
                "found_matches": len(matching_nodes)
            }
        }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        graph_data = storage.load_knowledge_graph()
        
        if not graph_data:
            return {"error": "Knowledge graph does not exist"}
        
        node_types = {}
        for node in graph_data.get("nodes", []):
            node_type = node.get("type", "UNKNOWN")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        relation_types = {}
        for edge in graph_data.get("edges", []):
            relation = edge.get("relation", "UNKNOWN")
            relation_types[relation] = relation_types.get(relation, 0) + 1
        
        return {
            "total_nodes": len(graph_data.get("nodes", [])),
            "total_edges": len(graph_data.get("edges", [])),
            "node_types": node_types,
            "relation_types": relation_types,
            "metadata": graph_data.get("metadata", {})
        }