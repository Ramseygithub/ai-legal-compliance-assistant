import os
import requests
import json
from typing import List, Dict, Any, Optional

class AlibabaBailianClient:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv("ALIBABA_API_KEY")
        self.qwen_model = os.getenv("QWEN_MODEL", "qwen-turbo")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v1")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        
        # Set vector dimensions based on model
        self.vector_dim = self._get_vector_dimension()
        
        if not self.api_key:
            print("Warning: ALIBABA_API_KEY environment variable not set, AI features will be unavailable")
            self.api_key = "dummy_key"  # Set dummy key to avoid startup errors
    
    def _get_vector_dimension(self) -> int:
        """Get vector dimension based on embedding model"""
        model_dimensions = {
            "text-embedding-v1": 1536,
            "text-embedding-v2": 1536,
            "text-embedding-v3": 1024,
            "text-embedding-v4": 1024,
            "text-embedding-ada-002": 1536
        }
        return model_dimensions.get(self.embedding_model, 1024)
    
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def check_api_status(self) -> Dict[str, Any]:
        """Check Alibaba Cloud API status and account balance"""
        if self.api_key == "dummy_key":
            return {
                "status": "not_configured",
                "message": "API key not configured",
                "can_use_api": False
            }
        
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        payload = {
            "model": self.qwen_model,
            "input": {
                "messages": [{"role": "user", "content": "test"}]
            },
            "parameters": {"max_tokens": 1}
        }
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            
            if response.status_code == 200:
                return {
                    "status": "active",
                    "message": "API is working properly",
                    "can_use_api": True
                }
            elif response.status_code == 400:
                error_data = response.json()
                if error_data.get("code") == "Arrearage":
                    return {
                        "status": "insufficient_balance",
                        "message": "Account balance insufficient. Please recharge at https://dashscope.console.aliyun.com/",
                        "can_use_api": False,
                        "error_code": "Arrearage"
                    }
            
            return {
                "status": "error",
                "message": f"API error: {response.status_code}",
                "can_use_api": False
            }
            
        except Exception as e:
            return {
                "status": "connection_error",
                "message": f"Cannot connect to API: {str(e)}",
                "can_use_api": False
            }
    
    def generate_text(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.1) -> str:
        if self.api_key == "dummy_key":
            return f"AI features unavailable - API key not configured. Original query: {prompt[:100]}..."
            
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        payload = {
            "model": self.qwen_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.8
            }
        }
        
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            
            # Check for specific API errors
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("code") == "Arrearage":
                    error_msg = "⚠️ Alibaba Cloud API Error: Account balance insufficient. Please recharge your account at https://dashscope.console.aliyun.com/"
                    print(error_msg)
                    return error_msg
            
            response.raise_for_status()
            
            result = response.json()
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            else:
                return f"API response format error, please check configuration. Error: {result}"
                
        except requests.exceptions.RequestException as e:
            return f"API call failed: {str(e)}"
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.api_key == "dummy_key":
            # Return dummy vectors for testing with correct dimensions
            import random
            return [[random.random() for _ in range(self.vector_dim)] for _ in texts]
            
        url = f"{self.base_url}/services/embeddings/text-embedding/text-embedding"
        
        embeddings = []
        
        for text in texts:
            payload = {
                "model": self.embedding_model,
                "input": {
                    "texts": [text]
                }
            }
            
            try:
                response = requests.post(url, headers=self._get_headers(), json=payload)
                response.raise_for_status()
                
                result = response.json()
                if "output" in result and "embeddings" in result["output"]:
                    embeddings.append(result["output"]["embeddings"][0]["embedding"])
                else:
                    # Return dummy vector with correct dimensions
                    import random
                    embeddings.append([random.random() for _ in range(self.vector_dim)])
                    
            except requests.exceptions.RequestException as e:
                # Return dummy vector with correct dimensions
                import random
                embeddings.append([random.random() for _ in range(self.vector_dim)])
        
        return embeddings
    
    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        prompt = f"""
Please extract key legal entities from the following legal text, including:
1. Legal articles (e.g., Article X, Section Y)
2. Types of violations
3. Penalty measures
4. Responsible parties
5. Related concepts or terms

Text:
{text}

Please return results in JSON format:
{{
    "legal_articles": [...],
    "violations": [...],
    "penalties": [...],
    "responsible_parties": [...],
    "related_concepts": [...]
}}
"""
        
        response = self.generate_text(prompt, max_tokens=800)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "legal_articles": [],
                    "violations": [],
                    "penalties": [],
                    "responsible_parties": [],
                    "related_concepts": []
                }
        except:
            return {
                "legal_articles": [],
                "violations": [],
                "penalties": [],
                "responsible_parties": [],
                "related_concepts": []
            }
    
    def analyze_compliance(self, business_data: str, regulations: str) -> Dict[str, Any]:
        prompt = f"""
As a legal compliance expert, please analyze whether the following business data violates relevant regulations:

Relevant Regulations:
{regulations[:1500]}

Business Data:
{business_data}

Please analyze and return in JSON format:
{{
    "compliance_status": "Compliant/Violation/Risk",
    "confidence": 0.0-1.0,
    "violations": [...],
    "recommendations": [...],
    "risk_level": "Low/Medium/High"
}}
"""
        
        response = self.generate_text(prompt, max_tokens=1000)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "compliance_status": "Unknown",
                    "confidence": 0.5,
                    "violations": [],
                    "recommendations": ["Manual review required"],
                    "risk_level": "Medium"
                }
        except:
            return {
                "compliance_status": "Unknown",
                "confidence": 0.5,
                "violations": [],
                "recommendations": ["Manual review required"],
                "risk_level": "Medium"
            }