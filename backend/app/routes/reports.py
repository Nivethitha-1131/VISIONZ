"""
VISIONZ — Reports Routes
Only returns reports created from real video analysis sessions.
"""

import json
from fastapi import APIRouter, Depends
from ..database import get_db
from ..middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/")
def list_reports(report_type: str = None, user=Depends(get_current_user)):
    conn = get_db()
    cur  = conn.cursor()
    if report_type:
        rows = cur.execute(
            "SELECT * FROM reports WHERE user_id=? AND report_type=? ORDER BY created_at DESC",
            (user["id"], report_type)
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM reports WHERE user_id=? ORDER BY created_at DESC",
            (user["id"],)
        ).fetchall()
    conn.close()

    reports = []
    for r in rows:
        d = dict(r)
        try:
            d["cat_counts"] = json.loads(d.get("cat_counts") or "{}")
        except Exception:
            d["cat_counts"] = {}
        reports.append(d)

    return {"reports": reports, "total": len(reports)}


@router.get("/{report_id}")
def get_report(report_id: int, user=Depends(get_current_user)):
    conn = get_db()
    cur  = conn.cursor()
    row  = cur.execute(
        "SELECT * FROM reports WHERE id=? AND user_id=?", (report_id, user["id"])
    ).fetchone()
    conn.close()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return dict(row)


@router.post("/")
def create_report(data: dict, user=Depends(get_current_user)):
    """Called by frontend after video analysis completes."""
    conn = get_db()
    cur  = conn.cursor()
    cat_json = json.dumps(data.get("cat_counts", {}))
    cur.execute("""
        INSERT INTO reports
        (user_id, report_name, report_type, period_start, period_end,
         total_scanned, total_defects, quality_score, cat_counts)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        user["id"],
        data.get("report_name", "Video Analysis Report"),
        data.get("report_type", "session"),
        data.get("period_start"),
        data.get("period_end"),
        data.get("total_scanned", 0),
        data.get("total_defects", 0),
        data.get("quality_score", 100),
        cat_json,
    ))
    conn.commit()
    report_id = cur.lastrowid
    conn.close()
    return {"success": True, "report_id": report_id}


@router.post("/{report_id}/download")
def mark_download(report_id: int, user=Depends(get_current_user)):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE reports SET downloaded=downloaded+1 WHERE id=? AND user_id=?",
        (report_id, user["id"])
    )
    conn.commit()
    conn.close()
    return {"success": True}
