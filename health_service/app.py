from flask import Flask
from routes.ping import bp as ping_bp
from routes.hello import bp as hello_bp
from routes.post import bp as post_bp
from routes.postgres import bp as postgres_bp
from routes.openai import bp as openai_bp
import os

def create_app():
    app = Flask(__name__)

    # Default metadata (can be overridden by environment variables)
    app.config.setdefault("SERVICE_NAME", os.getenv("SERVICE_NAME", "my-service"))
    app.config.setdefault("ENVIRONMENT", os.getenv("ENVIRONMENT", "dev"))
    app.config.setdefault("SERVICE_VERSION", os.getenv("SERVICE_VERSION", "v0.1"))

    # Register blueprints
    app.register_blueprint(ping_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(postgres_bp)
    app.register_blueprint(openai_bp)

    return app


if __name__ == "__main__":
    app = create_app()

    port = int(__import__("os").environ.get("PORT", 8080))
    # Enable debug only in dev environment
    debug_mode = app.config["ENVIRONMENT"].lower() == "dev"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
