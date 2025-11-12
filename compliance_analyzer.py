from typing import Dict, Any, List, Optional
from app.rag_service import RAGService
from app.ai_client import AlibabaBailianClient
from app.vector_service import VectorEmbeddingService
from app.storage import storage
import json
import uuid
from datetime import datetime

class ComplianceAnalyzer:
    def __init__(self):
        self.rag_service = RAGService()
        self.ai_client = AlibabaBailianClient()
        self.vector_service = VectorEmbeddingService()
        
        self.risk_levels = {
            "Low": {"score_range": (0.0, 0.3), "color": "green"},
            "Medium": {"score_range": (0.3, 0.7), "color": "orange"},
            "High": {"score_range": (0.7, 1.0), "color": "red"}
        }
    
    def analyze_compliance(self, business_data: Dict[str, Any], analysis_scope: str = "Comprehensive Analysis") -> Dict[str, Any]:
        """Comprehensive compliance analysis"""
        analysis_id = str(uuid.uuid4())
        
        try:
            business_description = self._extract_business_description(business_data)
            
            relevant_regulations = self._find_relevant_regulations(business_description)
            
            risk_assessment = self._assess_compliance_risk(business_description, relevant_regulations)
            
            detailed_analysis = self._perform_detailed_analysis(business_data, relevant_regulations)
            
            recommendations = self._generate_recommendations(risk_assessment, detailed_analysis)
            
            result = {
                "analysis_id": analysis_id,
                "timestamp": datetime.now().isoformat(),
                "business_data": business_data,
                "compliance_status": risk_assessment["compliance_status"],
                "overall_risk_level": risk_assessment["risk_level"],
                "risk_score": risk_assessment["risk_score"],
                "violated_regulations": detailed_analysis["violations"],
                "warning_items": detailed_analysis["warnings"],
                "recommendations": recommendations,
                "relevant_regulations": [reg["content"][:200] + "..." for reg in relevant_regulations[:3]],
                "analysis_details": {
                    "regulations_checked": len(relevant_regulations),
                    "violations_found": len(detailed_analysis["violations"]),
                    "warnings_issued": len(detailed_analysis["warnings"]),
                    "analysis_scope": analysis_scope
                }
            }
            
            self._save_analysis_result(analysis_id, result)
            
            return result
        
        except Exception as e:
            return {
                "analysis_id": analysis_id,
                "error": f"Compliance analysis failed: {str(e)}",
                "compliance_status": "Analysis Failed",
                "risk_level": "Unknown"
            }
    
    def _extract_business_description(self, business_data: Dict[str, Any]) -> str:
        """Extract description text from business data"""
        description_parts = []
        
        if "business_type" in business_data:
            description_parts.append(f"Business Type: {business_data['business_type']}")
        
        if "price_strategy" in business_data:
            description_parts.append(f"Price Strategy: {business_data['price_strategy']}")
        
        if "market_behavior" in business_data:
            description_parts.append(f"Market Behavior: {business_data['market_behavior']}")
        
        if "description" in business_data:
            description_parts.append(f"Detailed Description: {business_data['description']}")
        
        for key, value in business_data.items():
            if key not in ["business_type", "price_strategy", "market_behavior", "description"] and isinstance(value, str):
                description_parts.append(f"{key}: {value}")
        
        return "\n".join(description_parts) if description_parts else str(business_data)
    
    def _find_relevant_regulations(self, business_description: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find relevant legal regulations"""
        return self.vector_service.find_similar_segments(business_description, top_k)
    
    def _assess_compliance_risk(self, business_description: str, regulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess compliance risk"""
        if not regulations:
            return {
                "compliance_status": "Unable to Determine",
                "risk_level": "Medium",
                "risk_score": 0.5,
                "reason": "No relevant regulations found"
            }
        
        relevant_reg_text = "\n\n".join([reg["content"] for reg in regulations[:5]])
        
        analysis_result = self.ai_client.analyze_compliance(business_description, relevant_reg_text)
        
        compliance_status = analysis_result.get("compliance_status", "Unknown")
        risk_level = analysis_result.get("risk_level", "Medium")
        confidence = analysis_result.get("confidence", 0.5)
        
        risk_score = self._calculate_risk_score(compliance_status, risk_level, confidence)
        
        return {
            "compliance_status": compliance_status,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "confidence": confidence,
            "analysis_result": analysis_result
        }
    
    def _calculate_risk_score(self, compliance_status: str, risk_level: str, confidence: float) -> float:
        """Calculate risk score"""
        base_scores = {
            "Compliant": 0.1,
            "Violation": 0.9,
            "Risk": 0.6,
            "Unknown": 0.5
        }
        
        risk_multipliers = {
            "Low": 0.3,
            "Medium": 0.6,
            "High": 1.0
        }
        
        base_score = base_scores.get(compliance_status, 0.5)
        risk_multiplier = risk_multipliers.get(risk_level, 0.6)
        
        risk_score = base_score * risk_multiplier * confidence
        
        return round(min(max(risk_score, 0.0), 1.0), 2)
    
    def _perform_detailed_analysis(self, business_data: Dict[str, Any], regulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform detailed compliance analysis"""
        violations = []
        warnings = []
        
        for regulation in regulations[:5]:
            similarity_score = regulation.get("similarity_score", 0)
            
            if similarity_score > 0.7:
                violation_check = self._check_specific_violation(business_data, regulation)
                if violation_check["is_violation"]:
                    violations.append(violation_check)
                elif violation_check["has_risk"]:
                    warnings.append(violation_check)
        
        return {
            "violations": violations,
            "warnings": warnings
        }
    
    def _check_specific_violation(self, business_data: Dict[str, Any], regulation: Dict[str, Any]) -> Dict[str, Any]:
        """Check for specific violations"""
        reg_content = regulation["content"]
        business_desc = self._extract_business_description(business_data)
        
        prompt = f"""Please analyze whether the following business behavior violates specific legal regulations:

Legal Regulation:
{reg_content}

Business Behavior:
{business_desc}

Please determine:
1. Does it constitute a clear violation?
2. Are there compliance risks?
3. What are the specific violation points or risk points?

Please respond in JSON format:
{{
    "is_violation": true/false,
    "has_risk": true/false,
    "violation_reason": "reason for violation",
    "risk_points": ["risk point 1", "risk point 2"],
    "severity": "minor/moderate/severe"
}}"""
        
        try:
            response = self.ai_client.generate_text(prompt, max_tokens=800)
            
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                result = json.loads(response[start_idx:end_idx])
                result["regulation_content"] = reg_content[:200] + "..."
                result["similarity_score"] = regulation.get("similarity_score", 0)
                return result
        
        except:
            pass
        
        return {
            "is_violation": False,
            "has_risk": True,
            "violation_reason": "Requires manual review",
            "risk_points": ["Automated analysis has uncertainties"],
            "severity": "moderate",
            "regulation_content": reg_content[:200] + "...",
            "similarity_score": regulation.get("similarity_score", 0)
        }
    
    def _generate_recommendations(self, risk_assessment: Dict[str, Any], detailed_analysis: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        compliance_status = risk_assessment["compliance_status"]
        risk_level = risk_assessment["risk_level"]
        violations = detailed_analysis["violations"]
        warnings = detailed_analysis["warnings"]
        
        if compliance_status == "Violation":
            recommendations.append("Immediately stop related business activities and conduct comprehensive compliance remediation")
            
            for violation in violations:
                if violation.get("severity") == "severe":
                    recommendations.append(f"Serious violation: {violation.get('violation_reason', 'Not specified')}")
        
        elif compliance_status == "Risk":
            recommendations.append("Recommend conducting compliance review and improving related systems and processes")
            
            for warning in warnings:
                recommendations.append(f"Risk alert: {', '.join(warning.get('risk_points', []))}")
        
        if risk_level == "High":
            recommendations.append("Recommend consulting professional legal advisors to develop detailed compliance remediation plans")
        
        elif risk_level == "Medium":
            recommendations.append("Recommend strengthening internal compliance training and establishing regular self-inspection mechanisms")
        
        else:
            recommendations.append("Continue maintaining good compliance practices and regularly update related knowledge")
        
        general_recommendations = [
            "Establish comprehensive compliance management system",
            "Regularly update regulations and conduct training",
            "Set up compliance inspection and reporting mechanisms",
            "Establish communication channels with regulatory authorities"
        ]
        
        recommendations.extend(general_recommendations[:2])
        
        return recommendations[:8]
    
    def _save_analysis_result(self, analysis_id: str, result: Dict[str, Any]):
        """Save analysis results"""
        try:
            file_path = f"./data/compliance_analysis_{analysis_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save analysis results: {e}")
    
    def get_compliance_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get compliance analysis history"""
        import os
        import glob
        
        try:
            pattern = "./data/compliance_analysis_*.json"
            files = glob.glob(pattern)
            files.sort(key=os.path.getmtime, reverse=True)
            
            history = []
            for file_path in files[:limit]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        summary = {
                            "analysis_id": data.get("analysis_id"),
                            "timestamp": data.get("timestamp"),
                            "compliance_status": data.get("compliance_status"),
                            "risk_level": data.get("overall_risk_level"),
                            "violations_count": len(data.get("violated_regulations", [])),
                        }
                        history.append(summary)
                except:
                    continue
            
            return history
        
        except Exception as e:
            return []
    
    def compare_compliance_results(self, analysis_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple compliance analysis results"""
        results = []
        
        for analysis_id in analysis_ids:
            try:
                file_path = f"./data/compliance_analysis_{analysis_id}.json"
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append(data)
            except:
                continue
        
        if not results:
            return {"error": "No valid analysis results found"}
        
        comparison = {
            "total_analyses": len(results),
            "compliance_distribution": {},
            "risk_level_distribution": {},
            "common_violations": {},
            "trend_analysis": []
        }
        
        for result in results:
            status = result.get("compliance_status", "Unknown")
            comparison["compliance_distribution"][status] = \
                comparison["compliance_distribution"].get(status, 0) + 1
            
            risk = result.get("overall_risk_level", "Unknown")
            comparison["risk_level_distribution"][risk] = \
                comparison["risk_level_distribution"].get(risk, 0) + 1
        
        return comparison