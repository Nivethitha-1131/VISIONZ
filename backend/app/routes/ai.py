"""
VISIONZ — AI Analysis Route
Supports Claude API, local Llama via Ollama, and built-in local analyzer
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
import urllib.request
import urllib.error
import json
import os
from typing import Optional
from datetime import datetime

from app.services.llama_service import get_llama_service
from app.services.yolo_service import get_yolo_service
from app.config import settings

router = APIRouter()

# Get Claude API key from settings (configured in .env)
CLAUDE_API_KEY = settings.ANTHROPIC_API_KEY.strip() if settings.ANTHROPIC_API_KEY else ""

# API key is configured if we have a valid key
API_KEY_CONFIGURED = bool(CLAUDE_API_KEY and len(CLAUDE_API_KEY) > 20)


def generate_local_analysis(
    framesScanned: int,
    defectCount: int,
    passCount: int,
    defectRate: str,
    catCounts: dict,
    filename: str = "Unknown Video"
) -> dict:
    """Generate AI quality analysis using local logic (no API required)"""
    
    try:
        rate_val = float(defectRate.replace("%", "").strip())
    except Exception:
        rate_val = 0.0
    
    # Determine verdict based on defect rate
    if rate_val == 0:
        verdict = "PASS"
        verdict_text = "No defects detected — excellent production quality."
    elif rate_val < 2:
        verdict = "PASS"
        verdict_text = "Minimal defects — within acceptable tolerances."
    elif rate_val < 5:
        verdict = "WARNING"
        verdict_text = "Moderate defect rate — immediate action recommended."
    else:
        verdict = "CRITICAL"
        verdict_text = "High defect rate — production line requires shutdown for inspection."
    
    # Identify top defect causes
    sorted_defects = sorted(catCounts.items(), key=lambda x: x[1], reverse=True)
    top_defects = sorted_defects[:2]
    
    root_causes = []
    if sorted_defects:
        if sorted_defects[0][1] > 0:
            root_causes.append(f"• {sorted_defects[0][0]}: Primary defect type—{((sorted_defects[0][1] / defectCount * 100) if defectCount > 0 else 0):.0f}% of all defects")
        if len(sorted_defects) > 1 and sorted_defects[1][1] > 0:
            root_causes.append(f"• {sorted_defects[1][0]}: Secondary defect type—{((sorted_defects[1][1] / defectCount * 100) if defectCount > 0 else 0):.0f}% of all defects")
    
    if not root_causes:
        root_causes = ["• No significant defect patterns detected", "• Quality metrics within normal range"]
    
    # Generate recommendations based on defect type and rate
    recommendations = []
    
    if defectCount == 0:
        recommendations = [
            "1. Continue current production parameters—no adjustments needed",
            "2. Maintain routine maintenance schedule",
            "3. Log production batch as approved for shipment"
        ]
    elif rate_val < 2:
        recommendations = [
            "1. Maintain current production settings and material sourcing",
            "2. Schedule standard maintenance for equipment",
            "3. Document batch as acceptable for shipment"
        ]
    elif rate_val < 5:
        recommendations = [
            "1. Increase quality control inspection frequency to 10 min intervals",
            "2. Review recent material supplier changes or equipment calibration",
            "3. Halt further production until root cause identified"
        ]
    else:
        recommendations = [
            "1. STOP production immediately—conduct full equipment diagnostic",
            "2. Inspect raw material quality and temperature controls",
            "3. Recalibrate vision systems and reset production parameters"
        ]
    
    # Risk level assessment
    if rate_val == 0:
        risk_level = "Low"
        risk_text = "No quality risks detected—production is optimal."
    elif rate_val < 2:
        risk_level = "Low"
        risk_text = "Minimal risk—production meets quality standards."
    elif rate_val < 5:
        risk_level = "Medium"
        risk_text = "Moderate risk—increased monitoring required."
    else:
        risk_level = "High"
        risk_text = "Critical risk—immediate corrective action required."
    
    analysis_text = f"""VERDICT: {verdict} — {verdict_text}

ROOT CAUSES:
{chr(10).join(root_causes)}

RECOMMENDATIONS:
{chr(10).join(recommendations)}

RISK LEVEL: {risk_level} — {risk_text}

Summary: {framesScanned:,} frames analyzed. {defectCount} defects found ({defectRate}).
Batch Report: {filename}"""
    
    return {
        "analysis": analysis_text,
        "model": "visionz-local-analyzer",
        "timestamp": datetime.now().isoformat(),
    }


class AnalysisRequest(BaseModel):
    framesScanned: int
    defectCount:   int
    passCount:     int
    defectRate:    str
    catCounts:     dict
    filename:      str = "Unknown Video"
    use_llama:     Optional[bool] = False


@router.post("/analyze")
def analyze_defects(req: AnalysisRequest):
    """Receives defect summary, returns AI quality analysis via Claude or Llama."""

    rate_val = 0.0
    try:
        rate_val = float(req.defectRate.replace("%", "").strip())
    except Exception:
        pass

    # ── USE LLAMA IF REQUESTED ──
    if req.use_llama:
        print("[AI] Using Llama for analysis")
        llama_service = get_llama_service()
        result = llama_service.generate_analysis(
            framesScanned=req.framesScanned,
            defectCount=req.defectCount,
            passCount=req.passCount,
            defectRate=req.defectRate,
            catCounts=req.catCounts,
            filename=req.filename
        )
        return result

    # ── DEMO MODE ──
    if not API_KEY_CONFIGURED:
        print("[AI] Claude API key not configured, using local analyzer")
        result = generate_local_analysis(
            framesScanned=req.framesScanned,
            defectCount=req.defectCount,
            passCount=req.passCount,
            defectRate=req.defectRate,
            catCounts=req.catCounts,
            filename=req.filename
        )
        return result

    # ── REAL CLAUDE CALL ──
    cat_lines = "\n".join(
        f"    - {cat}: {count}"
        for cat, count in req.catCounts.items() if count > 0
    ) or "    - No defects detected"

    prompt = f"""You are an expert quality control analyst for an FMCG manufacturing plant.

Inspection just completed:
- Video: {req.filename}
- Frames Analyzed: {req.framesScanned:,}
- Defects Found: {req.defectCount}
- Frames Passed: {req.passCount}
- Defect Rate: {req.defectRate}

Defect Breakdown:
{cat_lines}

Provide a concise quality report with these exact sections:
VERDICT: [PASS / WARNING / CRITICAL] — one sentence
ROOT CAUSES: 2 bullet points on top defect causes
RECOMMENDATIONS: exactly 3 numbered action steps
RISK LEVEL: [Low / Medium / High] — one sentence action

Keep total response under 200 words. Be direct and practical."""

    payload = json.dumps({
        "model":      "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages":   [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    request_obj = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    print(f"[AI] Calling Claude API (key ends: ...{CLAUDE_API_KEY[-6:]})")

    try:
        with urllib.request.urlopen(request_obj, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["content"][0]["text"]
            print(f"[AI] Success — {len(text)} chars returned")
            return {"analysis": text, "model": "claude-sonnet-4-20250514"}

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[AI] Claude API HTTP {e.code}: {body[:300]}")
        # Parse error message from Anthropic
        try:
            err_detail = json.loads(body).get("error", {}).get("message", body[:100])
        except Exception:
            err_detail = body[:100]
        
        # Fall back to built-in local analyzer
        print(f"[AI] Falling back to local analyzer due to Claude error")
        local_result = generate_local_analysis(
            framesScanned=req.framesScanned,
            defectCount=req.defectCount,
            passCount=req.passCount,
            defectRate=req.defectRate,
            catCounts=req.catCounts,
            filename=req.filename
        )
        local_result["analysis"] += f"\n\n[System] Claude API error ({e.code}). Using built-in analyzer."
        local_result["model"] = "visionz-local-fallback"
        print(f"[AI] Local analyzer generated report successfully")
        return local_result

    except urllib.error.URLError as e:
        print(f"[AI] Network error: {e.reason}")
        # Fall back to built-in local analyzer
        print(f"[AI] Falling back to local analyzer due to network error")
        local_result = generate_local_analysis(
            framesScanned=req.framesScanned,
            defectCount=req.defectCount,
            passCount=req.passCount,
            defectRate=req.defectRate,
            catCounts=req.catCounts,
            filename=req.filename
        )
        local_result["analysis"] += f"\n\n[System] Network error connecting to Claude API. Using built-in analyzer."
        local_result["model"] = "visionz-local-fallback"
        print(f"[AI] Local analyzer generated report successfully")
        return local_result

    except Exception as e:
        print(f"[AI] Unexpected error: {type(e).__name__}: {e}")
        # Fall back to built-in local analyzer
        print(f"[AI] Falling back to local analyzer due to unexpected error")
        local_result = generate_local_analysis(
            framesScanned=req.framesScanned,
            defectCount=req.defectCount,
            passCount=req.passCount,
            defectRate=req.defectRate,
            catCounts=req.catCounts,
            filename=req.filename
        )
        local_result["analysis"] += f"\n\n[System] Error connecting to Claude API. Using built-in analyzer."
        local_result["model"] = "visionz-local-fallback"
        print(f"[AI] Local analyzer generated report successfully")
        return local_result


@router.get("/models")
def get_available_models():
    """Get information about available AI models"""
    llama_service = get_llama_service()
    yolo_service = get_yolo_service()
    
    return {
        "models": [
            {
                "id": "claude",
                "name": "Claude (Anthropic)",
                "status": "available" if API_KEY_CONFIGURED else "not-configured",
                "type": "analysis"
            },
            {
                "id": "llama",
                "name": "Llama 2 (Local)",
                "status": "available" if llama_service.available else "unavailable",
                "type": "analysis",
                "note": "Requires Ollama running locally"
            },
            {
                "id": "yolov6",
                "name": "YOLOv6 Detection",
                "status": "available" if yolo_service.available else "demo-mode",
                "type": "detection"
            }
        ]
    }


@router.post("/detect/video")
def detect_video(
    video_path: str,
    max_frames: Optional[int] = Query(None, description="Max frames to process"),
    skip_frames: int = Query(1, description="Process every Nth frame")
):
    """Run YOLOv6 detection on a video file"""
    yolo_service = get_yolo_service()
    result = yolo_service.detect_video(video_path, max_frames, skip_frames)
    return result


@router.get("/detect/health")
def detect_health():
    """Check health of detection service"""
    yolo_service = get_yolo_service()
    return {
        "service": "yolov6",
        "available": yolo_service.available,
        "model": yolo_service.model_name if yolo_service.available else "disabled",
        "device": str(yolo_service.device) if yolo_service.available else None
    }




def build_demo_analysis(req: AnalysisRequest, rate: float = 0.0) -> str:
    """Realistic demo analysis from real defect numbers."""
    verdict = "CRITICAL" if rate > 5 else "WARNING" if rate > 2 else "PASS"
    risk    = "High"     if rate > 5 else "Medium"  if rate > 2 else "Low"

    top_cats = sorted(
        [(k, v) for k, v in req.catCounts.items() if v > 0],
        key=lambda x: x[1], reverse=True
    )
    top1 = top_cats[0][0] if top_cats else "General Defects"
    top2 = top_cats[1][0] if len(top_cats) > 1 else "Packaging Issues"

    risk_action = {
        "High":   "Immediate supervisor escalation required.",
        "Medium": "Monitor closely for next 2 shifts.",
        "Low":    "Continue standard monitoring protocol."
    }[risk]

    return f"""VERDICT: {verdict} — Defect rate of {req.defectRate} {'exceeds' if rate > 3 else 'is within'} acceptable threshold (≤3%).

ROOT CAUSES:
• {top1}: Likely caused by improper machine calibration or worn tooling. Inspect line immediately.
• {top2}: Usually indicates packaging material inconsistency or conveyor speed mismatch.

RECOMMENDATIONS:
1. Halt affected line station — inspect {top1} defect source and recalibrate
2. Cross-check packaging material batch against last approved supplier lot
3. Increase sampling rate to every 50 units until defect rate drops below 2%

RISK LEVEL: {risk} — {risk_action}

[Demo Mode — add your ANTHROPIC_API_KEY to ai.py for live Claude analysis]"""
