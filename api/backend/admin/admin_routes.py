from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

admin_routes = Blueprint("admin_routes", __name__)


# ------------------------------------------------------------
# GET  /admin     — list all admins
# POST /admin     — create a new admin record
# ------------------------------------------------------------
@admin_routes.route("/", methods=["GET"])
def get_all_admins():
    """
    Return all admin accounts with role, has_access, and linked user info.
    Alex-4
    """
    query = """
        SELECT a.admin_id, a.role, a.has_access,
               u.user_id, u.full_name, u.email, u.last_login
        FROM   admins a
        JOIN   users  u ON a.user_id = u.user_id
        ORDER  BY a.admin_id
    """
    cursor = get_db().cursor()
    cursor.execute(query)
    admins = cursor.fetchall()
    return make_response(jsonify(admins), 200)


@admin_routes.route("/", methods=["POST"])
def create_admin():
    """
    Create a new admin record linked to an existing user.
    Body JSON: { "user_id": int, "role": str, "has_access": 0|1 }
    Alex-4
    """
    data = request.get_json()
    user_id    = data.get("user_id")
    role       = data.get("role")
    has_access = data.get("has_access", 1)

    if not user_id or not role:
        return make_response(
            jsonify({"error": "user_id and role are required"}), 400
        )

    query = "INSERT INTO admins (has_access, role, user_id) VALUES (%s, %s, %s)"
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(query, (has_access, role, user_id))
    conn.commit()

    return make_response(
        jsonify({"message": "Admin created", "admin_id": cursor.lastrowid}), 201
    )


# ------------------------------------------------------------
# GET /admin/{admin_id}  — full admin detail
# PUT /admin/{admin_id}  — update role or has_access
# ------------------------------------------------------------
@admin_routes.route("/<int:admin_id>", methods=["GET"])
def get_admin(admin_id):
    """
    Return admin role, access level, linked user profile,
    and count of authored logs and reports.
    Alex-4
    """
    query = """
        SELECT a.admin_id, a.role, a.has_access,
               u.user_id, u.full_name, u.email, u.last_login,
               (SELECT COUNT(*) FROM system_logs  sl WHERE sl.creator_id = a.admin_id) AS log_count,
               (SELECT COUNT(*) FROM data_reports dr WHERE dr.creator_id = a.admin_id) AS report_count
        FROM   admins a
        JOIN   users  u ON a.user_id = u.user_id
        WHERE  a.admin_id = %s
    """
    cursor = get_db().cursor()
    cursor.execute(query, (admin_id,))
    admin = cursor.fetchone()

    if not admin:
        return make_response(jsonify({"error": "Admin not found"}), 404)
    return make_response(jsonify(admin), 200)


@admin_routes.route("/<int:admin_id>", methods=["PUT"])
def update_admin(admin_id):
    """
    Update role or toggle has_access for a specific admin.
    Body JSON: any subset of { "role": str, "has_access": 0|1 }
    Alex-4
    """
    data = request.get_json()
    fields = {k: data[k] for k in ("role", "has_access") if k in data}

    if not fields:
        return make_response(
            jsonify({"error": "Provide at least one of: role, has_access"}), 400
        )

    set_clause = ", ".join(f"{k} = %s" for k in fields)
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE admins SET {set_clause} WHERE admin_id = %s",
        (*fields.values(), admin_id),
    )
    conn.commit()

    return make_response(
        jsonify({"message": f"Admin {admin_id} updated successfully"}), 200
    )
