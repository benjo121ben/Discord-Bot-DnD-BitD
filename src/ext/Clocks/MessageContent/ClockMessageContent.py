import logging


from .AbstractMessageContent import AbstractMessageContent
from ..clock_data import Clock

logger = logging.getLogger('bot')


class ClockMessageContent(AbstractMessageContent):
    def __init__(self, clock: Clock, **kwargs):
        self.clock = clock
        self.kwargs = kwargs

    def get_message_content(self, extraction_function) -> dict:
        ret_dict = extraction_function(self.clock)
        for key, val in self.kwargs.items():
            ret_dict[key] = val
        return ret_dict

