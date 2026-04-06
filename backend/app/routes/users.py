"""
VISIONZ — Users Routes
GET  /api/users/profile
GET  /api/users/all          (admin only)
PUT  /api/users/profile
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.schemas import UserOut, UserUpdateRequest, ProfileResponse

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
def get_profile(authorization: str = Header(...)):
    """Get the logged-in user's full profile with session stats."""
    user = get_current_user(authorization)
    token = authorization[len("Bearer "):]

    conn = get_db()
    cur  = conn.cursor()

    # Get session info
    cur.execute(
        "SELECT login_time FROM sessions WHERE token = ? AND is_active = 1",
        (token,)
    )
    session = cur.fetchone()

    # Count reports downloaded by this user
    cur.execute(
        "SELECT SUM(downloaded) FROM reports WHERE user_id = ?",
        (user["id"],)
    )
    dl_row = cur.fetchone()
    reports_downloaded = dl_row[0] or 0

    # Count total sessions
    cur.execute(
        "SELECT COUNT(*) FROM sessions WHERE user_id = ?",
        (user["id"],)
    )
    session_count = cur.fetchone()[0] or 1

    conn.close()

    return ProfileResponse(
        id                 = user["id"],
        name               = user["name"],
        email              = user["email"],
        role               = user["role"],
        avatar             = user["avatar"],
        department         = user.get("department"),
        login_time         = session["login_time"] if session else None,
        reports_downloaded = reports_downloaded,
        session_count      = session_count,
    )


@router.put("/profile")
def update_profile(body: UserUpdateRequest, authorization: str = Header(...)):
    """Update the logged-in user's name or department."""
    user = get_current_user(authorization)
    conn = get_db()
    cur  = conn.cursor()

    updates = {}
    if body.name:       updates["name"]       = body.name
    if body.department: updates["department"] = body.department

    if not updates:
        conn.close()
        return {"message": "Nothing to update."}

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values     = list(updates.values()) + [user["id"]]
    cur.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully."}


@router.get("/all")
def get_all_users(user: dict = Depends(require_admin)):
    """Return all users — admin only."""
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT id, name, email, role, avatar, department, created_at, last_login FROM users")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"users": rows, "total": len(rows)}
