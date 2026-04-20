from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

data_report_routes = Blueprint("data_report_routes", __name__)


# ------------------------------------------------------------
# GET  /data_report  — list all reports (filterable)
# POST /data_report  — create and save a new report
# ------------------------------------------------------------
@data_report_routes.route("/", methods=["GET"])
def get_all_reports():
    """
    Return all saved data reports.
    Optional query params:
      ?creator_id=int
      ?keyword=str   (searches filter_criteria and description)
      ?from=YYYY-MM-DD  (created_at after)
      ?to=YYYY-MM-DD    (created_at before)
    Lauren-6
    """
    creator_id = request.args.get("creator_id")
    keyword    = request.args.get("keyword")
    from_date  = request.args.get("from")
    to_date    = request.args.get("to")

    query = """
        SELECT dr.report_id, dr.filter_criteria, dr.description,
               dr.create_at, dr.updated_at,
               dr.creator_id, u.full_name AS creator_name
        FROM   data_reports dr
        JOIN   admins a ON dr.creator_id = a.admin_id
        JOIN   users  u ON a.user_id     = u.user_id
        WHERE  1=1
    """
    params = []

    if creator_id:
        query += " AND dr.creator_id = %s"
        params.append(int(creator_id))
    if keyword:
        query += " AND (dr.filter_criteria LIKE %s OR dr.description LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if from_date:
        query += " AND dr.create_at >= %s"
        params.append(from_date)
    if to_date:
        query += " AND dr.create_at <= %s"
        params.append(to_date)

    query += " ORDER BY dr.updated_at DESC"

    cursor = get_db().cursor()
    cursor.execute(query, params)
    reports = cursor.fetchall()
    return make_response(jsonify(reports), 200)


@data_report_routes.route("/", methods=["POST"])
def create_report():
    """
    Create and save a new analytics report.
    Body JSON: { "filter_criteria": str, "description": str, "creator_id": int }
    Lauren-6
    """
    data = request.get_json()
    filter_criteria = data.get("filter_criteria", "")
    description     = data.get("description", "")
    creator_id      = data.get("creator_id")

    if not creator_id:
        return make_response(jsonify({"error": "creator_id is required"}), 400)

    query = """
        INSERT INTO data_reports (filter_criteria, description, creator_id)
        VALUES (%s, %s, %s)
    """
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(query, (filter_criteria, description, creator_id))
    conn.commit()

    return make_response(
        jsonify({"message": "Report created", "report_id": cursor.lastrowid}), 201
    )


# ------------------------------------------------------------
# GET    /data_report/{report_id}  — report detail
# PUT    /data_report/{report_id}  — update description or filters
# DELETE /data_report/{report_id}  — delete report + junction rows
# ------------------------------------------------------------
@data_report_routes.route("/<int:report_id>", methods=["GET"])
def get_report(report_id):
    """
    Return full detail for one report including attached applications.
    Lauren-6
    """
    cursor = get_db().cursor()

    cursor.execute(
        """
        SELECT dr.report_id, dr.filter_criteria, dr.description,
               dr.create_at, dr.updated_at, dr.creator_id,
               u.full_name AS creator_name
        FROM   data_reports dr
        JOIN   admins a ON dr.creator_id = a.admin_id
        JOIN   users  u ON a.user_id     = u.user_id
        WHERE  dr.report_id = %s
        """,
        (report_id,),
    )
    report = cursor.fetchone()
    if not report:
        return make_response(jsonify({"error": "Report not found"}), 404)

    # Fetch linked applications
    cursor.execute(
        """
        SELECT ar.application_id, ar.applicant_id,
               a.stage, a.status, a.application_date,
               jp.job_title
        FROM   application_reports ar
        JOIN   applications a  ON ar.application_id = a.application_id
                               AND ar.applicant_id   = a.applicant_id
        JOIN   job_posts    jp ON a.job_id           = jp.post_id
        WHERE  ar.report_id = %s
        """,
        (report_id,),
    )
    report["applications"] = cursor.fetchall()

    return make_response(jsonify(report), 200)


@data_report_routes.route("/<int:report_id>", methods=["PUT"])
def update_report(report_id):
    """
    Update description or filter_criteria. Triggers updated_at automatically.
    Body JSON: any subset of { "filter_criteria": str, "description": str }
    Lauren-6
    """
    data   = request.get_json()
    fields = {k: data[k] for k in ("filter_criteria", "description") if k in data}

    if not fields:
        return make_response(
            jsonify({"error": "Provide at least one of: filter_criteria, description"}),
            400,
        )

    set_clause = ", ".join(f"{k} = %s" for k in fields)
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE data_reports SET {set_clause} WHERE report_id = %s",
        (*fields.values(), report_id),
    )
    conn.commit()

    return make_response(
        jsonify({"message": f"Report {report_id} updated successfully"}), 200
    )


@data_report_routes.route("/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    """
    Delete a report and its application_reports junction rows.
    Lauren-6
    """
    conn   = get_db()
    cursor = conn.cursor()

    # Remove junction rows first (FK constraint)
    cursor.execute(
        "DELETE FROM application_reports WHERE report_id = %s", (report_id,)
    )
    cursor.execute(
        "DELETE FROM data_reports WHERE report_id = %s", (report_id,)
    )
    conn.commit()

    return make_response(
        jsonify({"message": f"Report {report_id} deleted"}), 200
    )


# ------------------------------------------------------------
# GET    /data_report/{report_id}/applications  — linked apps
# POST   /data_report/{report_id}/applications  — attach apps
# DELETE /data_report/{report_id}/applications/{application_id}
# ------------------------------------------------------------
@data_report_routes.route("/<int:report_id>/applications", methods=["GET"])
def get_report_applications(report_id):
    """
    Return all applications attached to this report.
    Lauren-6
    """
    query = """
        SELECT ar.application_id, ar.applicant_id,
               a.stage, a.status, a.application_date,
               jp.job_title, u.full_name AS applicant_name
        FROM   application_reports ar
        JOIN   applications a  ON ar.application_id = a.application_id
                               AND ar.applicant_id   = a.applicant_id
        JOIN   job_posts    jp ON a.job_id           = jp.post_id
        JOIN   job_seekers  js ON a.applicant_id     = js.seeker_id
        JOIN   users        u  ON js.user_id         = u.user_id
        WHERE  ar.report_id = %s
    """
    cursor = get_db().cursor()
    cursor.execute(query, (report_id,))
    return make_response(jsonify(cursor.fetchall()), 200)


@data_report_routes.route("/<int:report_id>/applications", methods=["POST"])
def attach_applications(report_id):
    """
    Attach one or more applications to this report.
    Body JSON: { "applications": [{ "application_id": int, "applicant_id": int }, ...] }
    Lauren-6
    """
    data = request.get_json()
    apps = data.get("applications", [])

    if not apps:
        return make_response(jsonify({"error": "applications list is required"}), 400)

    conn   = get_db()
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT IGNORE INTO application_reports (report_id, application_id, applicant_id) VALUES (%s, %s, %s)",
        [(report_id, a["application_id"], a["applicant_id"]) for a in apps],
    )
    conn.commit()

    return make_response(
        jsonify({"message": f"{cursor.rowcount} application(s) attached to report {report_id}"}),
        201,
    )


@data_report_routes.route(
    "/<int:report_id>/applications/<int:application_id>", methods=["DELETE"]
)
def detach_application(report_id, application_id):
    """
    Remove a specific application from this report.
    Does NOT delete the application itself.
    Lauren-6
    """
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM application_reports WHERE report_id = %s AND application_id = %s",
        (report_id, application_id),
    )
    conn.commit()

    return make_response(
        jsonify({"message": f"Application {application_id} removed from report {report_id}"}),
        200,
    )
