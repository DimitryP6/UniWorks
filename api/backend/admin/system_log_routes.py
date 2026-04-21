from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

system_log_routes = Blueprint("system_log_routes", __name__)


# ------------------------------------------------------------
# GET  /system_log  — list all logs (filterable)
# POST /system_log  — add a new log entry
# ------------------------------------------------------------
@system_log_routes.route("/", methods=["GET"])
def get_all_logs():
    """
    Return all system logs ordered by most recent.
    Optional query params:
      ?status=open|resolved
      ?error_code=str
      ?from=YYYY-MM-DD
      ?to=YYYY-MM-DD
    Alex-6
    """
    status     = request.args.get("status")
    error_code = request.args.get("error_code")
    from_date  = request.args.get("from")
    to_date    = request.args.get("to")

    query = """
        SELECT sl.log_id, sl.error_code, sl.error_description,
               sl.resolved_at, sl.resolution_status,
               sl.creator_id, u.full_name AS creator_name
        FROM   system_logs sl
        JOIN   admins a ON sl.creator_id = a.admin_id
        JOIN   users  u ON a.user_id     = u.user_id
        WHERE  1=1
    """
    params = []

    if status:
        query += " AND sl.resolution_status = %s"
        params.append(status)
    if error_code:
        query += " AND sl.error_code LIKE %s"
        params.append(f"%{error_code}%")
    if from_date:
        query += " AND sl.resolved_at >= %s"
        params.append(from_date)
    if to_date:
        query += " AND sl.resolved_at <= %s"
        params.append(to_date)

    query += " ORDER BY sl.log_id DESC"

    cursor = get_db().cursor()
    cursor.execute(query, params)
    logs = cursor.fetchall()
    return make_response(jsonify(logs), 200)


@system_log_routes.route("/", methods=["POST"])
def create_log():
    """
    Add a new system log entry.
    Body JSON: {
        "error_code": str,
        "error_description": str,
        "resolution_status": str,   # "open" or "resolved"
        "creator_id": int,
        "resolved_at": "YYYY-MM-DD" # optional, omit if still open
    }
    Alex-4, Alex-6
    """
    data = request.get_json()

    error_code        = data.get("error_code")
    error_description = data.get("error_description")
    resolution_status = data.get("resolution_status", "open")
    creator_id        = data.get("creator_id")
    resolved_at       = data.get("resolved_at")  # may be None

    if not error_code or not error_description or not creator_id:
        return make_response(
            jsonify({"error": "error_code, error_description, and creator_id are required"}),
            400,
        )

    query = """
        INSERT INTO system_logs
               (error_code, error_description, resolved_at, resolution_status, creator_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        query, (error_code, error_description, resolved_at, resolution_status, creator_id)
    )
    conn.commit()

    return make_response(
        jsonify({"message": "Log entry created", "log_id": cursor.lastrowid}), 201
    )


# ------------------------------------------------------------
# GET /system_log/{log_id}  — full detail for one log
# PUT /system_log/{log_id}  — mark as resolved or update status
# (DELETE is intentionally not supported — logs are append-only)
# ------------------------------------------------------------
@system_log_routes.route("/<int:log_id>", methods=["GET"])
def get_log(log_id):
    """
    Return full detail for a specific log entry.
    Alex-6
    """
    query = """
        SELECT sl.log_id, sl.error_code, sl.error_description,
               sl.resolved_at, sl.resolution_status,
               sl.creator_id, u.full_name AS creator_name,
               u.email AS creator_email
        FROM   system_logs sl
        JOIN   admins a ON sl.creator_id = a.admin_id
        JOIN   users  u ON a.user_id     = u.user_id
        WHERE  sl.log_id = %s
    """
    cursor = get_db().cursor()
    cursor.execute(query, (log_id,))
    log = cursor.fetchone()

    if not log:
        return make_response(jsonify({"error": "Log entry not found"}), 404)
    return make_response(jsonify(log), 200)


@system_log_routes.route("/<int:log_id>", methods=["PUT"])
def update_log(log_id):
    """
    Update resolution_status and/or resolved_at for a log entry.
    Typical use: mark an open issue as resolved.
    Body JSON: any subset of {
        "resolution_status": "open"|"resolved",
        "resolved_at": "YYYY-MM-DD",
        "error_description": str
    }
    Alex-6
    """
    data = request.get_json()
    fields = {
        k: data[k]
        for k in ("resolution_status", "resolved_at", "error_description")
        if k in data
    }

    if not fields:
        return make_response(
            jsonify({"error": "Provide at least one field to update"}), 400
        )

    set_clause = ", ".join(f"{k} = %s" for k in fields)
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE system_logs SET {set_clause} WHERE log_id = %s",
        (*fields.values(), log_id),
    )
    conn.commit()

    return make_response(
        jsonify({"message": f"Log {log_id} updated successfully"}), 200
    )


# ------------------------------------------------------------
# GET /system_log/duplicates  — identify duplicate applications
#                               (Alex-1: surface before admin deletes)
# ------------------------------------------------------------
@system_log_routes.route("/duplicates", methods=["GET"])
def get_duplicate_applications():
    """
    Return duplicate application records grouped by applicant + job.
    Admin reviews these before calling DELETE /application.
    Alex-1
    """
    query = """
        SELECT a1.applicant_id,
               a1.job_id,
               COUNT(*) AS duplicate_count,
               GROUP_CONCAT(a1.application_id ORDER BY a1.application_id) AS application_ids
        FROM   applications a1
        GROUP  BY a1.applicant_id, a1.job_id
        HAVING COUNT(*) > 1
        ORDER  BY duplicate_count DESC
    """
    cursor = get_db().cursor()
    cursor.execute(query)
    duplicates = cursor.fetchall()
    return make_response(jsonify(duplicates), 200)
