import logging
import sys

from quart import Quart
from quart_cors import cors

from app.config import get_settings
from app.presentation.api.routes import api_bp


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger('app.infrastructure').setLevel(logging.INFO)
    logging.getLogger('app.presentation').setLevel(logging.INFO)
    

def create_app() -> Quart:

    setup_logging()

    app = Quart(__name__)

    app = cors(
        app,
        allow_origin=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    app.register_blueprint(api_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
