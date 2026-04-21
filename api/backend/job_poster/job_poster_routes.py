from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Create a Blueprint for job_poster routes
job_posts = Blueprint("job_poster", __name__)

@job_posts.route("/job_post", methods=["POST"])
def create_job_post():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /job_post')
        data = request.get_json()

        required_fields = ["job_title", "job_duration", "city_state", "poster_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """
            INSERT INTO job_posts (job_title, job_salary, job_description, job_duration,
            job_link, city_state, attendance_type, is_active, poster_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["job_title"],
            data.get("job_salary"),
            data.get("job_description"),
            data["job_duration"],
            data.get("job_link"),
            data["city_state"],
            data.get("attendance_type"),
            data.get("is_active", 1),
            data["poster_id"]
        ))

        get_db().commit()
        return jsonify({"message": "Job post created successfully", "post_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_job_post: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>", methods=["GET"])
def get_job_post(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /job_post/{post_id}')

        query = """
            SELECT jp.*, jpo.company_name, jpo.industry
            FROM job_posts jp
            JOIN job_posters jpo ON jp.poster_id = jpo.poster_id
            WHERE jp.post_id = %s
        """
        cursor.execute(query, (post_id,))
        job_post = cursor.fetchone()

        if not job_post:
            return jsonify({"error": "Job post not found"}), 404

        return jsonify(job_post), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_job_post: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>", methods=["PUT"])
def update_job_post(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /job_post/{post_id}')
        data = request.get_json()

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        allowed_fields = ["job_title", "job_salary", "job_description", "job_duration",
                          "job_link", "city_state", "attendance_type", "is_active"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(post_id)
        query = f"UPDATE job_posts SET {', '.join(update_fields)} WHERE post_id = %s"
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Job post updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_job_post: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>", methods=["DELETE"])
def delete_job_post(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /job_post/{post_id}')

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        cursor.execute("DELETE FROM job_posts WHERE post_id = %s", (post_id,))
        get_db().commit()

        return jsonify({"message": "Job post deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_job_post: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/job_links", methods=["GET"])
def get_job_links(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /job_post/{post_id}/job_links')

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        cursor.execute("SELECT * FROM job_links WHERE post_id = %s", (post_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_job_links: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/job_links", methods=["POST"])
def add_job_link(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /job_post/{post_id}/job_links')
        data = request.get_json()

        if "job_link" not in data:
            return jsonify({"error": "Missing required field: job_link"}), 400

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        cursor.execute(
            "INSERT INTO job_links (post_id, job_link) VALUES (%s, %s)",
            (post_id, data["job_link"])
        )
        get_db().commit()

        return jsonify({"message": "Job link added successfully"}), 201
    except Error as e:
        current_app.logger.error(f'Database error in add_job_link: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/job_links", methods=["DELETE"])
def delete_job_link(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /job_post/{post_id}/job_links')
        data = request.get_json()

        if "job_link" not in data:
            return jsonify({"error": "Missing required field: job_link"}), 400

        cursor.execute(
            "DELETE FROM job_links WHERE post_id = %s AND job_link = %s",
            (post_id, data["job_link"])
        )
        get_db().commit()

        return jsonify({"message": "Job link removed successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_job_link: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/job_limit", methods=["GET"])
def get_job_limit(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /job_post/{post_id}/job_limit')

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        cursor.execute("SELECT * FROM job_limits WHERE job_id = %s", (post_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_job_limit: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/job_limit", methods=["POST"])
def create_job_limit(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /job_post/{post_id}/job_limit')
        data = request.get_json()

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        query = """
            INSERT INTO job_limits (max_count, college, min_gpa, university, job_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get("max_count"),
            data.get("college"),
            data.get("min_gpa"),
            data.get("university"),
            post_id
        ))
        get_db().commit()

        return jsonify({"message": "Job limit created successfully", "limit_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_job_limit: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/job_limit", methods=["PUT"])
def update_job_limit(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /job_post/{post_id}/job_limit')
        data = request.get_json()

        cursor.execute("SELECT job_id FROM job_limits WHERE job_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job limit not found"}), 404

        allowed_fields = ["max_count", "college", "min_gpa", "university"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(post_id)
        query = f"UPDATE job_limits SET {', '.join(update_fields)} WHERE job_id = %s"
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Job limit updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_job_limit: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_poster/<int:poster_id>", methods=["GET"])
def get_job_poster(poster_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /job_poster/{poster_id}')

        query = """
            SELECT jpo.poster_id, jpo.company_name, jpo.industry,
                   u.email, u.full_name,
                   cw.website_link
            FROM job_posters jpo
            JOIN users u ON jpo.user_id = u.user_id
            LEFT JOIN company_websites cw ON jpo.poster_id = cw.poster_id
            WHERE jpo.poster_id = %s
        """
        cursor.execute(query, (poster_id,))
        poster = cursor.fetchone()

        if not poster:
            return jsonify({"error": "Job poster not found"}), 404

        return jsonify(poster), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_job_poster: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/job_post/<int:post_id>/applications", methods=["GET"])
def get_applications_for_post(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /job_post/{post_id}/applications')

        cursor.execute("SELECT post_id FROM job_posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Job post not found"}), 404

        query = """
            SELECT a.application_id,
                   a.application_date,
                   a.stage,
                   a.status,
                   a.cover_letter,
                   u.full_name,
                   u.email,
                   js.phone_number,
                   js.city_state,
                   js.major,
                   js.degree_level,
                   js.graduation_year,
                   r.education,
                   r.work_experience,
                   r.personal_project,
                   r.hobby
            FROM applications a
            JOIN job_seekers js ON a.applicant_id = js.seeker_id
            JOIN users u ON js.user_id = u.user_id
            JOIN resumes r ON a.resume_id = r.resume_id
            WHERE a.job_id = %s
            ORDER BY a.application_date DESC
        """
        cursor.execute(query, (post_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_applications_for_post: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@job_posts.route("/application/<int:application_id>/activity", methods=["POST"])
def add_application_activity(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /application/{application_id}/activity')
        data = request.get_json()

        cursor.execute(
            "SELECT application_id FROM applications WHERE application_id = %s",
            (application_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        required_fields = ["activity_date", "type"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor.execute(
            """INSERT INTO activities (activity_date, notes, type, status, application_id)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                data["activity_date"],
                data.get("notes"),
                data["type"],
                data.get("status", "Waiting"),
                application_id
            )
        )
        get_db().commit()
        return jsonify({"message": "Activity added successfully"}), 201

    except Error as e:
        current_app.logger.error(f'Database error in add_application_activity: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
