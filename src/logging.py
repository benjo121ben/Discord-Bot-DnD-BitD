import pathlib
import logging
import os
import sys

main_path = pathlib.Path(__file__).parent.resolve()


class StreamFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - (%(filename)s:%(lineno)d)\n%(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging():
    logpath = os.path.join(main_path, f'..{os.sep}logs')
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)

    fhandler = logging.FileHandler(filename=os.path.join(main_path, f'{logpath}{os.sep}debug.log'), mode='w', encoding='utf-8')
    fhandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - (%(filename)s:%(lineno)d)\n%(message)s "))
    logger.addHandler(fhandler)

    soutputhandler = logging.StreamHandler(stream=sys.stdout)
    soutputhandler.setFormatter(StreamFormatter())
    logger.addHandler(soutputhandler)

    return logger