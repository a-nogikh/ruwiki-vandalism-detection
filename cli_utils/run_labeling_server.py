import click
import logging
from labeling_interface.server import app


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

def get_command():
    @click.command()
    def run_labeling_server():
        logger.debug("running the server")
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    
    return run_labeling_server
