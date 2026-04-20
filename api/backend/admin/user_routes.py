from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

user_routes = Blueprint("user_routes", __name__)


# ------------------------------------------------------------
# GET  /user        — list all users (filter: is_active, user_type, last_login)
# PUT  /user        — bulk-archive inactive users
# ------------------------------------------------------------
@user_routes.route("/", methods=["GET"])
def get_all_users():
    """
    Return all users with is_active, last_login, user_type.
    Optional query params:
      ?is_active=0|1
      ?user_type=admin|job_seeker|job_poster
      ?inactive_before=YYYY-MM-DD  (last_login before this date)
    Alex-2, Alex-3
    """
    is_active      = request.args.get("is_active")
    user_type      = request.args.get("user_type")
    inactive_before = request.args.get("inactive_before")

    query = """
        SELECT user_id, full_name, email, user_type,
               is_active, created_at, last_login
        FROM   users
        WHERE  1=1
    """
    params = []

    if is_active is not None:
        query += " AND is_active = %s"
        params.append(int(is_active))
    if user_type:
        query += " AND user_type = %s"
        params.append(user_type)
    if inactive_before:
        query += " AND last_login < %s"
        params.append(inactive_before)

    query += " ORDER BY last_login DESC"

    cursor = get_db().cursor()
    cursor.execute(query, params)
    users = cursor.fetchall()
    return make_response(jsonify(users), 200)


@user_routes.route("/", methods=["PUT"])
def archive_inactive_users():
    """
    Bulk-archive users whose last_login is before a given date.
    Body JSON: { "inactive_before": "YYYY-MM-DD" }
    Alex-2
    """
    data = request.get_json()
    inactive_before = data.get("inactive_before")

    if not inactive_before:
        return make_response(
            jsonify({"error": "inactive_before date is required"}), 400
        )

    query = "UPDATE users SET is_active = 0 WHERE last_login < %s"
    cursor = get_db().cursor()
    cursor.execute(query, (inactive_before,))
    get_db().commit()

    return make_response(
        jsonify({"message": f"Archived users inactive before {inactive_before}",
                 "rows_affected": cursor.rowcount}),
        200,
    )


# ------------------------------------------------------------
# GET /user/{user_id}   — return full profile for one user
# PUT /user/{user_id}   — update profile fields or is_active
# ------------------------------------------------------------
@user_routes.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Return user profile including linked seeker/poster/admin record.
    Alex-5
    """
    query = """
        SELECT u.user_id, u.full_name, u.email, u.user_type,
               u.is_active, u.created_at, u.last_login,
               js.seeker_id, js.major, js.city_state,
               js.phone_number, js.degree_level, js.graduation_year
        FROM   users u
        LEFT JOIN job_seekers js ON u.user_id = js.user_id
        WHERE  u.user_id = %s
    """
    cursor = get_db().cursor()
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    return make_response(jsonify(user), 200)


@user_routes.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update user fields (is_active, user_type) and/or linked
    job_seekers fields (major, degree_level, city_state).
    Body JSON: any subset of updatable fields.
    Alex-2, Alex-5
    """
    data = request.get_json()
    conn   = get_db()
    cursor = conn.cursor()

    # Update users table fields if provided
    user_fields = {k: data[k] for k in ("is_active", "user_type", "full_name", "email")
                   if k in data}
    if user_fields:
        set_clause = ", ".join(f"{k} = %s" for k in user_fields)
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = %s",
            (*user_fields.values(), user_id),
        )

    # Update job_seekers table fields if provided
    seeker_fields = {k: data[k]
                     for k in ("major", "degree_level", "city_state",
                                "phone_number", "graduation_year", "profile_picture")
                     if k in data}
    if seeker_fields:
        set_clause = ", ".join(f"{k} = %s" for k in seeker_fields)
        cursor.execute(
            f"""
            UPDATE job_seekers js
              JOIN users u ON js.user_id = u.user_id
            SET {set_clause}
            WHERE u.user_id = %s
            """,
            (*seeker_fields.values(), user_id),
        )

    conn.commit()
    return make_response(
        jsonify({"message": f"User {user_id} updated successfully"}), 200
    )


# ------------------------------------------------------------
# GET /user/validate  — surface job_seekers rows with blank
#                       required fields (Alex-3)
# ------------------------------------------------------------
@user_routes.route("/validate", methods=["GET"])
def validate_seeker_records():
    """
    Return job_seekers rows with missing required fields.
    Alex-3
    """
    query = """
        SELECT js.seeker_id, u.full_name, u.email,
               js.major, js.city_state, js.phone_number,
               js.degree_level, js.graduation_year
        FROM   job_seekers js
        JOIN   users u ON js.user_id = u.user_id
        WHERE  js.major       = ''
           OR  js.city_state  = ''
           OR  js.phone_number = ''
           OR  js.degree_level = ''
           OR  js.graduation_year IS NULL
    """
    cursor = get_db().cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return make_response(jsonify(rows), 200)
