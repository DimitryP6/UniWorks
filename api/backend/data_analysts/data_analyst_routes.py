from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

data_analysts = Blueprint("data_analyst", __name__)


## Get all applications with filters for major, industry, stage, and graduation year.
@data_analysts.route("/application", methods=["GET"])
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


## Get all activities for a specific application, and can filter by type.
@data_analysts.route("/application/<int:application_id>/activity", methods=["GET"])
def get_application_activities(application_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /data_analyst/application/{application_id}/activity")
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


## Get all data reports.
@data_analysts.route("/data_report", methods=["GET"])
def get_data_reports():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /data_analyst/data_report")
        query = """
        SELECT * 
        FROM data_reports
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(result)} data reports")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_data_reports: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Creates and saves a new data report, given description, filter_criteria, and creator_id.
@data_analysts.route("/data_report", methods=["POST"])
def create_data_report():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /data_analyst/data_report")
        data = request.get_json()
        required_fields = ["description", "filter_criteria", "creator_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        query = """
        INSERT INTO data_reports (description, filter_criteria, creator_id)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            data["description"],
            data["filter_criteria"],
            data["creator_id"]
        ))
        get_db().commit()
        return jsonify({
            "message": "Data report created successfully",
            "report_id": cursor.lastrowid
        }), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_data_report: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get detailed information about a specific report.
@data_analysts.route("/data_report/<int:report_id>", methods=["GET"])
def get_data_report(report_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /data_analyst/data_report/{report_id}")
        query = """
        SELECT *
        FROM data_reports
        WHERE report_id = %s
        """
        cursor.execute(query, (report_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_data_report: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Update description or filter criteria for a specific report.
@data_analysts.route("/data_report/<int:report_id>", methods=["PUT"])
def update_data_report(report_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /data_analyst/data_report/{report_id}")
        data = request.get_json()
        query = """
        SELECT *
        FROM data_reports
        WHERE report_id = %s
        """
        cursor.execute(query, (report_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Data report not found"}), 404
        
        allowed_fields = ["description", "filter_criteria"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        params.append(report_id)
        query = f"""
        UPDATE data_reports
        SET {', '.join(update_fields)}
        WHERE report_id = %s
        """
        cursor.execute(query, params)
        get_db().commit()
        return jsonify({"message": "Report updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_data_report: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Delete a specific saved report.
@data_analysts.route("/data_report/<int:report_id>", methods=["DELETE"])
def delete_data_report(report_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /data_analyst/data_report/{report_id}")
        query = """
        SELECT * 
        FROM data_reports
        WHERE report_id = %s
        """
        cursor.execute(query, (report_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Data report not found"}), 404

        query = """
        DELETE FROM application_reports
        WHERE report_id = %s
        """
        cursor.execute(query, (report_id,))
        query = """
        DELETE FROM data_reports
        WHERE report_id = %s
        """
        cursor.execute(query, (report_id,))
        get_db().commit()
        return jsonify({"message": "Report deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_data_report: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


## Get aggregated application trends with filters for major, industry, graduation year, and stage.
@data_analysts.route("/application/trends", methods=["GET"])
def get_application_trends():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /data_analyst/application/trends")
        major = request.args.get("major")
        industry = request.args.get("industry")
        grad_year = request.args.get("grad_year")
        stage = request.args.get("stage")
        query = """
        SELECT js.major, js.graduation_year, jp.industry, a.stage, a.status,
               COUNT(*) AS total_applications
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
        if grad_year:
            query += " AND YEAR(js.graduation_year) = %s"
            params.append(grad_year)
        if stage:
            query += " AND a.stage = %s"
            params.append(stage)
        query += """
        GROUP BY js.major, js.graduation_year, jp.industry, a.stage, a.status
        ORDER BY total_applications DESC
        """
        cursor.execute(query, params)
        result = cursor.fetchall()
        current_app.logger.info(f"Retrieved trends for {len(result)} groups")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_application_trends: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()