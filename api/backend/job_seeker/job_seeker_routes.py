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
        FROM job_posts
        WHERE 1 = 1
        """
        params = []
        if location:
            query += " AND city_state = %s"
            params.append(location)
        if salary:
            query += " AND job_salary >= %s"
            params.append(salary)
        if title:
            query += " AND job_title LIKE %s"
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


## Get detailed information for a specific job post.
@job_seekers.route("/job_post/<int:post_id>", methods=["GET"])
def get_job_post(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/job_post/{post_id}")
        query = """
        SELECT *
        FROM job_posts
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
        SELECT jp.company_name, jp.industry, u.email, cw.website_link
        FROM job_posters jp
        JOIN users u ON jp.user_id = u.user_id
        INNER JOIN company_websites cw ON jp.poster_id = cw.poster_id
        WHERE jp.poster_id = %s
        """
        cursor.execute(query, (poster_id,))
        result = cursor.fetchone()
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
        required_fields = ["applicant_id", "job_id", "resume_id", "application_date"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
        INSERT INTO applications (cover_letter, stage, status, application_date, applicant_id, job_id, resume_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get("cover_letter"),
            "Applied",
            "Waiting",
            data["application_date"],
            data["applicant_id"],
            data["job_id"],
            data["resume_id"]
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
@job_posts.route("/application/<int:application_id>", methods=["PUT"])
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
        query = """
        SELECT *
        FROM activities
        WHERE application_id = %s
        """
        cursor.execute(query, application_id)
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        query = """
        DELETE FROM activities
        WHERE application_id = %s
        """
        cursor.execute(query, application_id)
        query = """
        DELETE FROM applications
        WHERE application_id = %s
        """
        cursor.execute(query, application_id)
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
@job_seekers.route("/job_seeker/<int:seeker_id>", methods=["GET"])
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
@job_seekers.route("/job_seeker/<int:seeker_id>", methods=["PUT"])
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


## Get all applications submitted by a specific job seeker.
@job_seekers.route("/job_seeker/<int:seeker_id>/application", methods=["GET"])
def get_seeker_applications(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/job_seeker/{seeker_id}/application")
        query = """
        SELECT a.application_id, a.cover_letter, a.stage, a.status,
               a.application_date, p.job_title, p.city_state, p.attendance_type
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
        query = """
        SELECT *
        FROM resumes
        WHERE resume_id = %s
        """
        cursor.execute(query, resume_id)
        if not cursor.fetchone():
            return jsonify({"error": "Resume not found"}), 404
        query = """
        DELETE FROM personal_websites
        WHERE resume_id = %s AND website = %s
        """
        cursor.execute(query, (resume_id, data["website"]))
        get_db().commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Website not found"}), 404
        return jsonify({"message": "Personal website removed successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_personal_website: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()