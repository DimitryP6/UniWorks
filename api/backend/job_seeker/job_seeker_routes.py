from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Define the Blueprint at the top so it is available before use
job_seeker = Blueprint("job_seeker", __name__)

# --- Get all open job posts, with filters for location, salary, title, and attendance type (remote/hybrid/on-site)
@job_seeker.route("/job_post", methods=["GET"])
def get_job_posts():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /job_post (job seeker)")
        location = request.args.get("location")
        salary = request.args.get("salary")
        title = request.args.get("title")
        attendance_type = request.args.get("attendance_type")
        query = """
        SELECT * FROM JobPosts WHERE is_active = 1
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
        jobs = cursor.fetchall()
        return jsonify(jobs), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_job_posts: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Get all jobs (open and closed) for a job seeker (jobs they've applied to)
@job_seeker.route("/job_seeker/<int:seeker_id>/jobs", methods=["GET"])
def get_jobs_applied_to(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}/jobs")
        query = """
        SELECT jp.*, a.application_id, a.stage, a.status
        FROM Applications a
        JOIN JobPosts jp ON a.job_id = jp.post_id
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
@job_seeker.route("/job_seeker/<int:seeker_id>/application_status", methods=["GET"])
def get_application_status(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_seeker/{seeker_id}/application_status")
        query = """
        SELECT a.application_id, a.job_id, jp.title, a.stage, a.status, a.application_date
        FROM Applications a
        JOIN JobPosts jp ON a.job_id = jp.post_id
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


# --- Get employer contact info for a job post
@job_seeker.route("/job_post/<int:post_id>/employer_contact", methods=["GET"])
def get_employer_contact(post_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /job_post/{post_id}/employer_contact")
        query = """
        SELECT jp.poster_id, p.company_name, p.email, p.website
        FROM JobPosts jp
        JOIN JobPosters p ON jp.poster_id = p.poster_id
        WHERE jp.post_id = %s
        """
        cursor.execute(query, (post_id,))
        contact = cursor.fetchone()
        if not contact:
            return jsonify({"error": "Employer not found"}), 404
        return jsonify(contact), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_employer_contact: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Submit a new application (POST)
@job_seeker.route("/application", methods=["POST"])
def submit_application():
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        required_fields = ["seeker_id", "job_id", "resume_id", "cover_letter"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
            INSERT INTO Applications (seeker_id, job_id, resume_id, cover_letter, stage, status, application_date)
            VALUES (%s, %s, %s, %s, 'submitted', 'pending', NOW())
        """
        cursor.execute(query, (
            data["seeker_id"],
            data["job_id"],
            data["resume_id"],
            data["cover_letter"]
        ))
        get_db().commit()
        return jsonify({"message": "Application submitted", "application_id": cursor.lastrowid}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Add a new resume (POST)
@job_seeker.route("/resume", methods=["POST"])
def add_resume():
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        required_fields = ["seeker_id", "resume_text"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
            INSERT INTO Resumes (seeker_id, resume_text, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (
            data["seeker_id"],
            data["resume_text"]
        ))
        get_db().commit()
        return jsonify({"message": "Resume added", "resume_id": cursor.lastrowid}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Update a resume (PUT)
@job_seeker.route("/resume/<int:resume_id>", methods=["PUT"])
def update_resume(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        if "resume_text" not in data:
            return jsonify({"error": "Missing resume_text"}), 400
        query = "UPDATE Resumes SET resume_text = %s, updated_at = NOW() WHERE resume_id = %s"
        cursor.execute(query, (data["resume_text"], resume_id))
        get_db().commit()
        return jsonify({"message": "Resume updated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Delete an application (DELETE)
@job_seeker.route("/application/<int:application_id>", methods=["DELETE"])
def delete_application(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        query = "DELETE FROM Applications WHERE application_id = %s"
        cursor.execute(query, (application_id,))
        get_db().commit()
        return jsonify({"message": "Application deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# --- Delete a resume (DELETE)
@job_seeker.route("/resume/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        query = "DELETE FROM Resumes WHERE resume_id = %s"
        cursor.execute(query, (resume_id,))
        get_db().commit()
        return jsonify({"message": "Resume deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# GET /job_seeker/{seeker_id} - Return profile information for {seeker_id}
@job_seeker.route("/job_seeker/<int:seeker_id>", methods=["GET"])
def get_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM JobSeekers WHERE seeker_id = %s", (seeker_id,))
        seeker = cursor.fetchone()
        if not seeker:
            return jsonify({"error": "Job seeker not found"}), 404
        return jsonify(seeker), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# PUT /job_seeker/{seeker_id} - Update profile or fix incomplete record for {seeker_id}
@job_seeker.route("/job_seeker/<int:seeker_id>", methods=["PUT"])
def update_job_seeker(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    data = request.json
    try:
        # Example: update name, email, etc.
        update_fields = []
        params = []
        for field in ["name", "email", "major", "grad_year"]:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(seeker_id)
        query = f"UPDATE JobSeekers SET {', '.join(update_fields)} WHERE seeker_id = %s"
        cursor.execute(query, params)
        get_db().commit()
        return jsonify({"message": "Job seeker updated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# GET /job_seeker/{seeker_id}/application - Return all applications submitted by {seeker_id}
@job_seeker.route("/job_seeker/<int:seeker_id>/application", methods=["GET"])
def get_seeker_applications(seeker_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Applications WHERE seeker_id = %s", (seeker_id,))
        applications = cursor.fetchall()
        return jsonify(applications), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
