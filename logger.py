import logging

logger = logging.getLogger('sat_logger')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('SATScoreChecker.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)
