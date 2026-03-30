"""
VISIONZ — Llama Integration Service
Local LLM service using Ollama for quality control analysis
"""

import os
import json
from typing import Optional, Dict, Any
import requests
from datetime import datetime

# Ollama server configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL = os.environ.get("LLAMA_MODEL", "llama2")


class LlamaService:
    """Service for interacting with Llama via Ollama"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = LLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.available = self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[Llama] Ollama connection check failed: {e}")
            return False
    
    def generate_analysis(
        self,
        framesScanned: int,
        defectCount: int,
        passCount: int,
        defectRate: str,
        catCounts: Dict[str, int],
        filename: str = "Unknown Video"
    ) -> Dict[str, Any]:
        """Generate AI quality analysis using Llama"""
        
        if not self.available:
            return self._demo_analysis(framesScanned, defectCount, passCount, defectRate, catCounts, filename)
        
        rate_val = 0.0
        try:
            rate_val = float(defectRate.replace("%", "").strip())
        except Exception:
            pass
        
        # Build the defect breakdown
        cat_lines = "\n".join(
            f"    - {cat}: {count}"
            for cat, count in catCounts.items() if count > 0
        ) or "    - No defects detected"
        
        prompt = f"""You are an expert quality control analyst for an FMCG manufacturing plant.

Inspection just completed:
- Video: {filename}
- Frames Analyzed: {framesScanned:,}
- Defects Found: {defectCount}
- Frames Passed: {passCount}
- Defect Rate: {defectRate}

Defect Breakdown:
{cat_lines}

Provide a concise quality report with exactly these sections:
VERDICT: [PASS / WARNING / CRITICAL] — one sentence
ROOT CAUSES: 2 bullet points on top defect causes
RECOMMENDATIONS: exactly 3 numbered action steps
RISK LEVEL: [Low / Medium / High] — one sentence

Keep response under 200 words. Be direct and practical."""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "num_predict": 300,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis_text = data.get("response", "").strip()
                print(f"[Llama] Analysis generated successfully ({len(analysis_text)} chars)")
                return {
                    "analysis": analysis_text,
                    "model": f"llama2-local",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                print(f"[Llama] API error: {response.status_code}")
                return self._demo_analysis(framesScanned, defectCount, passCount, defectRate, catCounts, filename)
        
        except requests.exceptions.Timeout:
            print("[Llama] Request timeout - using demo analysis")
            return self._demo_analysis(framesScanned, defectCount, passCount, defectRate, catCounts, filename)
        except Exception as e:
            print(f"[Llama] Error: {e}")
            return self._demo_analysis(framesScanned, defectCount, passCount, defectRate, catCounts, filename)
    
    def _demo_analysis(
        self,
        framesScanned: int,
        defectCount: int,
        passCount: int,
        defectRate: str,
        catCounts: Dict[str, int],
        filename: str
    ) -> Dict[str, Any]:
        """Generate demo analysis when Llama is unavailable"""
        
        rate_val = 0.0
        try:
            rate_val = float(defectRate.replace("%", "").strip())
        except Exception:
            pass
        
        # Determine verdict based on defect rate
        if rate_val == 0:
            verdict = "PASS"
            risk = "Low"
        elif rate_val < 5:
            verdict = "WARNING"
            risk = "Medium"
        else:
            verdict = "CRITICAL"
            risk = "High"
        
        # Top defects
        sorted_defects = sorted(catCounts.items(), key=lambda x: x[1], reverse=True)
        top_causes = ""
        if sorted_defects:
            for i, (defect, count) in enumerate(sorted_defects[:2], 1):
                top_causes += f"\n    • {defect}: {count} occurrences detected"
        
        analysis = f"""VERDICT: {verdict} — Quality control review required for video {filename}

ROOT CAUSES:{top_causes if top_causes else """
    • No specific defects identified
    • System operating within acceptable parameters"""}

RECOMMENDATIONS:
    1. Review detected anomalies and validate detection accuracy
    2. Adjust camera angles or lighting if image quality issues detected
    3. Schedule maintenance if mechanical failures are suspected

RISK LEVEL: {risk} — {'Immediate action recommended' if risk == 'High' else 'Monitor closely for improvements' if risk == 'Medium' else 'Continue normal operations'}"""
        
        return {
            "analysis": analysis,
            "model": "llama2-demo",
            "timestamp": datetime.now().isoformat(),
            "status": "demo"
        }


# Global instance
_llama_instance: Optional[LlamaService] = None


def get_llama_service() -> LlamaService:
    """Get or create Llama service instance"""
    global _llama_instance
    if _llama_instance is None:
        _llama_instance = LlamaService()
    return _llama_instance


def initialize_llama():
    """Initialize Llama service"""
    global _llama_instance
    _llama_instance = LlamaService()
    print(f"[Llama] Service initialized - Available: {_llama_instance.available}")
    print(f"[Llama] Model: {_llama_instance.model}")
    print(f"[Llama] Base URL: {_llama_instance.base_url}")
