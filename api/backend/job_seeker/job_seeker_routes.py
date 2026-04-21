from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

job_seekers = Blueprint("job_seekers", __name__)


## Get all job posts with filters for location, salary, title, and attendance type.
@job_seekers.route("/job_post", methods=["GET"])
def get_job_posts():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /job_seeker/job_post")
        location = request.args.get("location")
        salary = request.args.get("salary")
        title = request.args.get("title")
        attendance_type = request.args.get("attendance_type")
        query = """
        SELECT *
        FROM ngo_db.job_posts
        WHERE 1 = 1
        """
        params = []
        if location:
            query += " AND location = %s"
            params.append(location)
        if salary:
            query += " AND salary >= %s"
            params.append(salary)
        if title:
            query += " AND title LIKE %s"
            params.append(f"%{title}%")
        if attendance_type:
            query += " AND attendance_type = %s"
            params.append(attendance_type)
        cursor.execute(query, params)
        result = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(result)} job posts")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_job_posts: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Get all jobs (open and closed) for a job seeker (jobs they've applied to)
@job_seekers.route("/<int:seeker_id>/jobs", methods=["GET"])
def get_jobs_applied_to(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}/jobs")
        query = """
        SELECT jp.*, a.application_id, a.stage, a.status
        FROM ngo_db.applications a
        JOIN ngo_db.job_posts jp ON a.job_id = jp.post_id
        WHERE a.seeker_id = %s
        ORDER BY a.application_date DESC
        """
        cursor.execute(query, (seeker_id,))
        jobs = cursor.fetchall()
        return jsonify(jobs), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_jobs_applied_to: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Get application status for a job seeker (all applications)
@job_seekers.route("/<int:seeker_id>/application_status", methods=["GET"])
def get_application_status(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}/application_status")
        query = """
        SELECT a.application_id, a.job_id, jp.title, a.stage, a.status, a.application_date
        FROM ngo_db.applications a
        JOIN ngo_db.job_posts jp ON a.job_id = jp.post_id
        WHERE a.seeker_id = %s
        ORDER BY a.application_date DESC
        """
        cursor.execute(query, (seeker_id,))
        status = cursor.fetchall()
        return jsonify(status), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_application_status: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

## Get detailed information for a specific job post.
@job_seekers.route("/job_post/<int:post_id>", methods=["GET"])
def get_job_post(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/job_post/{post_id}")
        query = """
        SELECT *
        FROM ngo_db.job_posts
        WHERE post_id = %s
        """
        cursor.execute(query, (post_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Job post not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_job_post: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

## Get company name, email, and website for a specific job poster.
@job_seekers.route("/job_poster/<int:poster_id>", methods=["GET"])
def get_job_poster(poster_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/job_poster/{poster_id}")
        query = """
        SELECT company_name, email, website
        FROM ngo_db.job_posters
        WHERE poster_id = %s
        """
        cursor.execute(query, (poster_id,))
        result = cursor.fetchall()
        if not result:
            return jsonify({"error": "Job poster not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_job_poster: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Submit a new application with cover letter and resume.
@job_seekers.route("/application", methods=["POST"])
def create_application():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /job_seeker/application")
        data = request.get_json()
        required_fields = ["seeker_id", "job_id", "resume_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
        INSERT INTO ngo_db.applications (seeker_id, job_id, resume_id, cover_letter, stage, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["seeker_id"],
            data["job_id"],
            data["resume_id"],
            data.get("cover_letter", ""),
            "submitted",
            "pending"
        ))
        get_db().commit()
        return jsonify({
            "message": "Application submitted successfully",
            "application_id": cursor.lastrowid
        }), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Add a new resume (POST)
@job_seekers.route("/resume", methods=["POST"])
def add_resume():
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        required_fields = ["seeker_id", "resume_text"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
            INSERT INTO ngo_db.resumes (seeker_id, resume_text, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (
            data["seeker_id"],
            data["resume_text"]
        ))
        get_db().commit()
        return jsonify({"message": "Resume added", "resume_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in add_resume: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

## Get detailed information for a specific application.
@job_seekers.route("/application/<int:application_id>", methods=["GET"])
def get_application(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/application/{application_id}")
        query = """
        SELECT *
        FROM ngo_db.applications
        WHERE application_id = %s
        """
        cursor.execute(query, (application_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Application not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

## Update stage and status for a specific application
@job_seekers.route("/application/<int:application_id>", methods=["PUT"])
def update_application(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /application/{application_id}')
        data = request.get_json()

        cursor.execute(
            "SELECT application_id FROM ngo_db.applications WHERE application_id = %s",
            (application_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        allowed_fields = ["stage", "status"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(application_id)
        query = f"UPDATE ngo_db.applications SET {', '.join(update_fields)} WHERE application_id = %s"
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Application updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_application: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Withdraw a specific application.
@job_seekers.route("/application/<int:application_id>", methods=["DELETE"])
def delete_application(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /job_seeker/application/{application_id}")
        cursor.execute(
            "SELECT application_id FROM ngo_db.applications WHERE application_id = %s",
            (application_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        cursor.execute(
            "DELETE FROM ngo_db.applications WHERE application_id = %s",
            (application_id,)
        )
        get_db().commit()
        return jsonify({"message": "Application withdrawn successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

## Get all activities for a specific application with filter by type.
@job_seekers.route("/application/<int:application_id>/activity", methods=["GET"])
def get_application_activities(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/application/{application_id}/activity")
        activity_type = request.args.get("type")
        query = """
        SELECT *
        FROM activities
        WHERE application_id = %s
        """
        params = [application_id]
        if activity_type:
            query += " AND type = %s"
            params.append(activity_type)
        query += " ORDER BY activity_date DESC"
        cursor.execute(query, params)
        result = cursor.fetchall()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_application_activities: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

## Get profile information for a specific job seeker.
@job_seekers.route("/<int:seeker_id>", methods=["GET"])
def get_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}")
        query = """
        SELECT seeker_id, name, email, major, grad_year
        FROM ngo_db.job_seekers
        WHERE seeker_id = %s
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
@job_seekers.route("/<int:seeker_id>", methods=["PUT"])
def update_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /job_seeker/{seeker_id}")
        data = request.get_json()
        allowed_fields = ["name", "email", "major", "grad_year"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(seeker_id)
        query = f"""
        UPDATE ngo_db.job_seekers
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


## Get all applications submitted by a specific job seeker.
@job_seekers.route("/<int:seeker_id>/application", methods=["GET"])
def get_seeker_applications(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}/application")
        query = """
        SELECT a.application_id, a.cover_letter, a.stage, a.status,
               a.application_date, p.title, p.location, p.attendance_type
        FROM ngo_db.applications a
        JOIN ngo_db.job_posts p ON a.job_id = p.post_id
        WHERE a.seeker_id = %s
        ORDER BY a.application_date DESC
        """
        cursor.execute(query, (seeker_id,))
        result = cursor.fetchall()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_seeker_applications: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get resume details for a specific resume.
@job_seekers.route("/resume/<int:resume_id>", methods=["GET"])
def get_resume(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/resume/{resume_id}")
        query = """
        SELECT *
        FROM ngo_db.resumes
        WHERE resume_id = %s
        """
        cursor.execute(query, (resume_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Resume not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_resume: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Update resume details for a specific resume.
@job_seekers.route("/resume/<int:resume_id>", methods=["PUT"])
def update_resume(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /job_seeker/resume/{resume_id}")
        data = request.get_json()
        allowed_fields = ["resume_text"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(resume_id)
        query = f"""
        UPDATE ngo_db.resumes
        SET {', '.join(update_fields)}
        WHERE resume_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()
        return jsonify({"message": "Resume updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_resume: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get all personal websites for a specific resume.
@job_seekers.route("/resume/<int:resume_id>/personal_website", methods=["GET"])
def get_personal_websites(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/resume/{resume_id}/personal_website")
        query = """
        SELECT *
        FROM ngo_db.resumes
        WHERE resume_id = %s
        """
        cursor.execute(query, (resume_id,))
        result = cursor.fetchall()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_personal_websites: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Add a new personal website to a specific resume.
@job_seekers.route("/resume/<int:resume_id>/personal_website", methods=["POST"])
def add_personal_website(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"POST /job_seeker/resume/{resume_id}/personal_website")
        data = request.get_json()
        if "website" not in data:
            return jsonify({"error": "Missing required field: website"}), 400
        query = """
        UPDATE ngo_db.resumes
        SET resume_text = CONCAT(resume_text, ' | Website: ', %s)
        WHERE resume_id = %s
        """
        cursor.execute(query, (data["website"], resume_id))
        get_db().commit()
        return jsonify({"message": "Personal website added successfully"}), 201
    except Error as e:
        current_app.logger.error(f"Database error in add_personal_website: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Remove a personal website from a specific resume.
@job_seekers.route("/resume/<int:resume_id>/personal_website", methods=["DELETE"])
def delete_personal_website(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /job_seeker/resume/{resume_id}/personal_website")
        data = request.get_json()
        if "website" not in data:
            return jsonify({"error": "Missing required field: website"}), 400
        cursor.execute(
            "SELECT resume_id FROM ngo_db.resumes WHERE resume_id = %s",
            (resume_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Resume not found"}), 404
        cursor.execute(
            "UPDATE ngo_db.resumes SET resume_text = REPLACE(resume_text, %s, '') WHERE resume_id = %s",
            (f" | Website: {data['website']}", resume_id)
        )
        get_db().commit()
        return jsonify({"message": "Personal website removed successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_personal_website: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
