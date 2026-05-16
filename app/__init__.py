from flask import Flask
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.main import main_bp
    from .routes.api import api_bp
    from .routes.export import export_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/export')

    return app
