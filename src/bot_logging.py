import pathlib
import logging
import os
import sys
from datetime import datetime

main_path = pathlib.Path(__file__).parent.resolve()
date_time_save_format = "%Y_%m_%d-%H_%M_%S"


class StreamFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(message)s"
    formaterr = "%(asctime)s - %(levelname)s - (%(filename)s:%(lineno)d):_///_%(message)s"
    testint = 80

    FORMATS = {
        logging.DEBUG: grey + formaterr + reset,
        logging.INFO: grey + formaterr + reset,
        logging.WARNING: yellow + formaterr + reset,
        logging.ERROR: red + formaterr + reset,
        logging.CRITICAL: bold_red + formaterr + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        formatted_string = formatter.format(record)
        return formatted_string.replace("_///_", " " * max(self.testint - len(formatted_string.split("_///_")[0]), 0))


def setup_logging():
    logpath = os.path.join(main_path, f'..{os.sep}logs')
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)

    fhandler = logging.FileHandler(filename=os.path.join(main_path,
                                                         f'{logpath}{os.sep}{datetime.now().replace(microsecond=0).strftime(date_time_save_format)}.log'),
                                   mode='w', encoding='utf-8')
    fhandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - (%(filename)s:%(lineno)d):    %(message)s "))
    logger.addHandler(fhandler)

    soutputhandler = logging.StreamHandler(stream=sys.stdout)
    soutputhandler.setFormatter(StreamFormatter())
    logger.addHandler(soutputhandler)

    return logger


def restart_logging():
    logging.getLogger('bot').handlers.clear()
    setup_logging()
