from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

admin_routes = Blueprint("admin_routes", __name__)


## Get all applications with filters for major, industry, stage, and graduation year.
@admin_routes.route("/application", methods=["GET"])
def get_applications():
    cursor = get_db().cursor(dictionary = True)
    try:
        current_app.logger.info("GET /data_analyst/application")
        major = request.args.get("major")
        industry = request.args.get("industry")
        stage = request.args.get("stage")
        grad_year = request.args.get("grad_year")
        query = """
        SELECT a.application_id, a.cover_letter, a.stage, a.status, a.application_date,
               js.major, js.graduation_year, jp.industry
        FROM applications a
        JOIN job_seekers js ON a.applicant_id = js.seeker_id
        JOIN job_posts p ON a.job_id = p.post_id
        JOIN job_posters jp ON p.poster_id = jp.poster_id
        WHERE 1 = 1
        """
        params = []
        if major:
            query += " AND js.major = %s"
            params.append(major)
        if industry:
            query += " AND jp.industry = %s"
            params.append(industry)
        if stage:
            query += " AND a.stage = %s"
            params.append(stage)
        if grad_year:
            query += " AND YEAR(js.graduation_year) = %s"
            params.append(grad_year)
        cursor.execute(query, params)
        result = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(result)} applications")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_applications: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get profile information for a specific job seeker.
@admin_routes.route("/job_seeker/<int:seeker_id>", methods=["GET"])
def get_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/job_seeker/{seeker_id}")
        query = """
        SELECT js.seeker_id, js.major, js.university, js.city_state,
               js.phone_number, js.degree_level, js.graduation_year,
               js.profile_picture, u.full_name, u.email
        FROM job_seekers js
        JOIN users u ON js.user_id = u.user_id
        WHERE js.seeker_id = %s
        """
        cursor.execute(query, (seeker_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Job seeker not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_job_seeker: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Update profile information for a specific job seeker.
@admin_routes.route("/job_seeker/<int:seeker_id>", methods=["PUT"])
def update_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /job_seeker/job_seeker/{seeker_id}")
        data = request.get_json()
        allowed_fields = ["major", "university", "city_state", "phone_number",
                          "degree_level", "graduation_year", "profile_picture"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(seeker_id)
        query = f"""
        UPDATE job_seekers
        SET {', '.join(update_fields)}
        WHERE seeker_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_job_seeker: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Delete a duplicate application by application_id.
@admin_routes.route("/application/<int:application_id>", methods=["DELETE"])
def delete_application(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /admin/application/{application_id}")
        query = """
        SELECT application_id
        FROM applications
        WHERE application_id = %s
        """
        cursor.execute(query, appplication_id)
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404
        query = """
        DELETE FROM activities
        WHERE application_id = %s
        """
        cursor.execute(query, appplication_id)
        query = """
        DELETE FROM application_reports
        WHERE application_id = %s
        """
        cursor.execute(query, appplication_id)
        query = """
        DELETE FROM applications
        WHERE application_id = %s
        """
        cursor.execute(query, appplication_id)
        get_db().commit()
        return jsonify({"message": "Duplicate application deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get all users with is_active and last_login information.
@admin_routes.route("/user", methods=["GET"])
def get_users():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /admin/user")
        query = """
        SELECT user_id, full_name, email, user_type, is_active, last_login
        FROM users
        ORDER BY last_login DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(result)} users")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_users: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Archive inactive users whose last login was over a year ago.
@admin_routes.route("/user", methods=["PUT"])
def archive_inactive_users():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("PUT /admin/user")
        query = """
        UPDATE users
        SET is_active = 0
        WHERE last_login < DATE_SUB(NOW(), INTERVAL 1 YEAR)
        AND is_active = 1
        """
        cursor.execute(query)
        get_db().commit()
        return jsonify({
            "message": "Inactive users archived successfully",
            "archived_count": cursor.rowcount
        }), 200
    except Error as e:
        current_app.logger.error(f"Database error in archive_inactive_users: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get admin information and role for a specific admin.
@admin_routes.route("/admin/<int:admin_id>", methods=["GET"])
def get_admin(admin_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /admin/admin/{admin_id}")
        query = """
        SELECT a.admin_id, a.role, a.has_access, u.full_name, u.email
        FROM admins a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.admin_id = %s
        """
        cursor.execute(query, (admin_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Admin not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_admin: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Update role or access for a specific admin.
@admin_routes.route("/admin/<int:admin_id>", methods=["PUT"])
def update_admin(admin_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /admin/admin/{admin_id}")
        data = request.get_json()
        allowed_fields = ["role", "has_access"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(admin_id)
        query = f"""
        UPDATE admins
        SET {', '.join(update_fields)}
        WHERE admin_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Admin not found"}), 404
        return jsonify({"message": "Admin updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_admin: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get all system logs ordered by most recent.
@admin_routes.route("/system_log", methods=["GET"])
def get_system_logs():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /admin/system_log")
        query = """
        SELECT *
        FROM system_logs
        ORDER BY log_id DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(result)} system logs")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_system_logs: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Add a new system log entry.
@admin_routes.route("/system_log", methods=["POST"])
def create_system_log():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /admin/system_log")
        data = request.get_json()
        required_fields = ["error_code", "error_description", "resolution_status", "creator_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
        INSERT INTO system_logs (error_code, error_description, resolution_status, creator_id)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["error_code"],
            data["error_description"],
            data["resolution_status"],
            data["creator_id"]
        ))
        get_db().commit()
        return jsonify({
            "message": "System log created successfully",
            "log_id": cursor.lastrowid
        }), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_system_log: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()