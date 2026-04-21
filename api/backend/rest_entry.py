from flask import Flask
from dotenv import load_dotenv
import os
import logging
from backend.db_connection import init_app as init_db

# The job seeker blueprints
from backend.job_seeker.job_seeker_routes import job_seekers
# The admin blueprints
from backend.admin.admin_routes import admin_routes
# The data analyst blueprint
from backend.data_analysts.data_analyst_routes import data_analysts
# The job poster blueprint
from backend.job_poster.job_poster_routes import job_posts

def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(job_seekers, url_prefix="/job_seeker")
    app.register_blueprint(job_posts, url_prefix="/job_poster") 
    app.register_blueprint(admin_routes, url_prefix="/admin")
    app.register_blueprint(data_analysts, url_prefix="/data_analyst")

    return app
