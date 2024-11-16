import logging
import datetime
import sys

# set up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# set up the stream handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# set up the formatter
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

# add the stream handler to the logger
logger.addHandler(stream_handler)