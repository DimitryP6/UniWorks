from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.simple.simple_routes import simple_routes
from backend.ngos.ngo_routes import ngos

# The admin blueprints
from backend.admin.user_routes import user_routes
from backend.admin.admin_routes import admin_routes
from backend.admin.data_report_routes import data_report_routes
from backend.admin.system_log_routes import system_log_routes

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
    app.register_blueprint(simple_routes)
    app.register_blueprint(ngos, url_prefix="/ngo")

    # Admin blueprints 
    app.register_blueprint(user_routes,          url_prefix="/user")
    app.register_blueprint(admin_routes,         url_prefix="/admin")
    app.register_blueprint(data_report_routes,   url_prefix="/data_report")
    app.register_blueprint(system_log_routes,    url_prefix="/system_log")

    return app
