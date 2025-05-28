import logging, sys
from google.cloud.logging_v2 import Client as GLogClient

def configure():
    # TODO: Implement proper Google Cloud Logging setup
    # client = GLogClient()
    # client.setup_logging()
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root.addHandler(handler) 