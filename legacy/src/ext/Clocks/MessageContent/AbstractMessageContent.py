import abc
from abc import ABC


class AbstractMessageContent(ABC):

    @abc.abstractmethod
    def get_message_content(self, extraction_function) -> dict:
        pass