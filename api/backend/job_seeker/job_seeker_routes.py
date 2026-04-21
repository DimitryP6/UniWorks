from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

job_seeker = Blueprint("job_seeker", __name__)

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
