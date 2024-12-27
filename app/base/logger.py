import logging
import os 

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=f'{ROOT_DIR}/logs/application.log',  # log to a file named 'app.log'
                    filemode='a',  # append to the log file if it exists, otherwise create it
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
logging.captureWarnings(True)

logger = logging.getLogger(__name__)