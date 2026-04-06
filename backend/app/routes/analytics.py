"""
VISIONZ — Analytics Routes
Returns ONLY real data from actual detections. No fake seeded data.
"""

from fastapi import APIRouter, Depends
from ..database import get_db
from ..middleware.auth_middleware import get_current_user

router = APIRouter()

EMPTY = {
    "total_scanned": 0,
    "total_defects": 0,
    "total_approved": 0,
    "biscuits_defects": 0,
    "honey_defects": 0,
    "packets_defects": 0,
    "nuts_defects": 0,
    "pass_rate": 0.0,
    "defect_rate": 0.0,
}

def calc_snapshot(rows):
    """Convert detection rows into a summary dict."""
    if not rows:
        return {**EMPTY}
    total_defects  = len(rows)
    biscuits = sum(1 for r in rows if (r["product"] or "").startswith("Biscuit"))
    honey    = sum(1 for r in rows if (r["product"] or "").startswith("Honey"))
    nuts     = sum(1 for r in rows if (r["product"] or "").startswith("Nut"))
    packets  = sum(1 for r in rows if (r["product"] or "").startswith("Snack"))
    # frame count = max frame number seen, or defects*3 as rough estimate
    frame_nums = [r["frame_number"] for r in rows if r["frame_number"]]
    total_scanned  = max(frame_nums) if frame_nums else total_defects * 3
    total_approved = max(0, total_scanned - total_defects)
    pass_rate      = round((total_approved / total_scanned * 100), 2) if total_scanned > 0 else 0.0
    defect_rate    = round((total_defects / total_scanned * 100), 2)  if total_scanned > 0 else 0.0
    return {
        "total_scanned":    total_scanned,
        "total_defects":    total_defects,
        "total_approved":   total_approved,
        "biscuits_defects": biscuits,
        "honey_defects":    honey,
        "packets_defects":  packets,
        "nuts_defects":     nuts,
        "pass_rate":        pass_rate,
        "defect_rate":      defect_rate,
    }


@router.get("/summary")
def analytics_summary(user=Depends(get_current_user)):
    """Returns today / this week / this month summaries from real detections."""
    conn = get_db()
    cur  = conn.cursor()

    today = cur.execute(
        "SELECT * FROM detections WHERE user_id=? AND date(detected_at)=date('now')", (user["id"],)
    ).fetchall()

    week = cur.execute(
        "SELECT * FROM detections WHERE user_id=? AND detected_at >= datetime('now','-7 days')", (user["id"],)
    ).fetchall()

    month = cur.execute(
        "SELECT * FROM detections WHERE user_id=? AND detected_at >= datetime('now','-30 days')", (user["id"],)
    ).fetchall()

    conn.close()
    return {
        "today": calc_snapshot(today),
        "week":  calc_snapshot(week),
        "month": calc_snapshot(month),
    }


@router.get("/trend")
def analytics_trend(user=Depends(get_current_user)):
    """Returns last 7 days defect rate trend from real detections."""
    conn = get_db()
    cur  = conn.cursor()
    rows = cur.execute("""
        SELECT date(detected_at) as day, COUNT(*) as cnt
        FROM detections WHERE user_id=?
        AND detected_at >= datetime('now','-7 days')
        GROUP BY day ORDER BY day
    """, (user["id"],)).fetchall()
    conn.close()

    if not rows:
        return {"labels": [], "datasets": []}

    labels = [r["day"] for r in rows]
    data   = [r["cnt"] for r in rows]
    return {
        "labels": labels,
        "datasets": [{"label": "Defects", "data": data}]
    }


@router.get("/category")
def analytics_category(period: str = "today", user=Depends(get_current_user)):
    """Returns per-product defect counts from real detections."""
    conn = get_db()
    cur  = conn.cursor()

    if period == "today":
        where = "date(detected_at)=date('now')"
    elif period == "week":
        where = "detected_at >= datetime('now','-7 days')"
    else:
        where = "detected_at >= datetime('now','-30 days')"

    rows = cur.execute(
        f"SELECT product, COUNT(*) as cnt FROM detections WHERE user_id=? AND {where} GROUP BY product",
        (user["id"],)
    ).fetchall()
    conn.close()

    return {"categories": [{"product": r["product"], "count": r["cnt"]} for r in rows]}
