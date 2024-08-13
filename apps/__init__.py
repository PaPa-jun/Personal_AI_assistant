from flask import Flask
from .config import config_map

def create_app(mode: str = "default"):
    """
    # Create app

    :param model: The mode to run this app.
    :return: The app.
    """

    app = Flask(__name__, template_folder="../templates", static_folder="../assets")
    app.config.from_object(config_map[mode])

    @app.route("/")
    def demo():
        return "Hello World!"

    return app