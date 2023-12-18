import logging
import sys
from project.frameworks_and_drivers.app import create_app
import pymongo
import logging

logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
logging.info(f'PyMongo version: {pymongo.__version__}')

app = create_app()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Run the application
    app.run()