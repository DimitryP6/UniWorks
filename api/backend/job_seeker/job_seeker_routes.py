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
        SELECT jp.post_id, jp.job_title, jp.job_salary, jp.job_description,
               jp.job_duration, jp.city_state, jp.attendance_type, jp.is_active,
               jpo.company_name, jpo.industry
        FROM job_posts jp
        JOIN job_posters jpo ON jp.poster_id = jpo.poster_id
        WHERE 1 = 1
        """
        params = []
        if location:
            query += " AND jp.city_state LIKE %s"
            params.append(f"%{location}%")
        if salary:
            query += " AND jp.job_salary >= %s"
            params.append(salary)
        if title:
            query += " AND jp.job_title LIKE %s"
            params.append(f"%{title}%")
        if attendance_type:
            query += " AND jp.attendance_type = %s"
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
        FROM applications a
        JOIN job_posts jp ON a.job_id = jp.post_id
        WHERE a.applicant_id = %s
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
        SELECT a.application_id, a.job_id, jp.job_title AS title,
               a.stage, a.status, a.application_date
        FROM applications a
        JOIN job_posts jp ON a.job_id = jp.post_id
        WHERE a.applicant_id = %s
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
        SELECT jp.*, jpo.company_name, jpo.industry
        FROM job_posts jp
        JOIN job_posters jpo ON jp.poster_id = jpo.poster_id
        WHERE jp.post_id = %s
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
        SELECT jpo.poster_id, jpo.company_name, jpo.industry,
               u.email, u.full_name, cw.website_link
        FROM job_posters jpo
        JOIN users u ON jpo.user_id = u.user_id
        LEFT JOIN company_websites cw ON jpo.poster_id = cw.poster_id
        WHERE jpo.poster_id = %s
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
        INSERT INTO applications (applicant_id, job_id, resume_id, cover_letter,
                                  stage, status, application_date)
        VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
        """
        cursor.execute(query, (
            data["seeker_id"],
            data["job_id"],
            data["resume_id"],
            data.get("cover_letter", ""),
            "Applied",
            "Waiting"
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
            INSERT INTO resumes (education, work_experience, personal_project, hobby, author_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get("education", ""),
            data.get("work_experience", ""),
            data.get("personal_project", ""),
            data.get("hobby", ""),
            data["seeker_id"]
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
        FROM applications
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
            "SELECT application_id FROM applications WHERE application_id = %s",
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
        query = f"UPDATE applications SET {', '.join(update_fields)} WHERE application_id = %s"
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
            "SELECT application_id FROM applications WHERE application_id = %s",
            (application_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        cursor.execute("DELETE FROM activities WHERE application_id = %s", (application_id,))
        cursor.execute("DELETE FROM application_reports WHERE application_id = %s", (application_id,))
        cursor.execute(
            "DELETE FROM applications WHERE application_id = %s",
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
@job_seekers.route("/<int:seeker_id>", methods=["PUT"])
def update_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /job_seeker/{seeker_id}")
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


## Get all applications submitted by a specific job seeker.
@job_seekers.route("/<int:seeker_id>/application", methods=["GET"])
def get_seeker_applications(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}/application")
        query = """
        SELECT a.application_id, a.cover_letter, a.stage, a.status,
               a.application_date, p.job_title AS title, p.city_state AS location,
               p.attendance_type
        FROM applications a
        JOIN job_posts p ON a.job_id = p.post_id
        WHERE a.applicant_id = %s
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
        FROM resumes
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
        allowed_fields = ["education", "work_experience", "personal_project", "hobby"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(resume_id)
        query = f"""
        UPDATE resumes
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


## Delete a specific resume.
@job_seekers.route("/resume/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /job_seeker/resume/{resume_id}")
        cursor.execute(
            "SELECT resume_id FROM resumes WHERE resume_id = %s",
            (resume_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Resume not found"}), 404

        cursor.execute("DELETE FROM personal_websites WHERE resume_id = %s", (resume_id,))
        cursor.execute("DELETE FROM resumes WHERE resume_id = %s", (resume_id,))
        get_db().commit()
        return jsonify({"message": "Resume deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_resume: {e}")
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
        FROM personal_websites
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
        INSERT INTO personal_websites (resume_id, website)
        VALUES (%s, %s)
        """
        cursor.execute(query, (resume_id, data["website"]))
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
            "SELECT resume_id FROM resumes WHERE resume_id = %s",
            (resume_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Resume not found"}), 404
        cursor.execute(
            "DELETE FROM personal_websites WHERE resume_id = %s AND website = %s",
            (resume_id, data["website"])
        )
        get_db().commit()
        return jsonify({"message": "Personal website removed successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_personal_website: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()