from .AbstractMessageContent import AbstractMessageContent


class DictMessageContent(AbstractMessageContent):

    def __init__(self, **kwargs):
        self.content_dict: dict = kwargs

    def get_message_content(self, _) -> dict:
        return self.content_dict

