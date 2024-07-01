import logging

from .MessageContent.AbstractMessageContent import AbstractMessageContent
from .MessageContent.ClockMessageContent import ClockMessageContent
from .MessageContent.DictMessageContent import DictMessageContent
from .clock_data import Clock

logger = logging.getLogger('bot')

MESSAGE_DELETION_DELAY: int = 10


def clean_clock_tag(clock_tag: str) -> str:
    return clock_tag.replace("_", "").strip().lower()


def create_clock_command_logic(clock_title: str, clock_size: int, clock_ticks: int = 0) -> AbstractMessageContent:
    new_clock = Clock(clock_title, clock_size, clock_ticks)
    return ClockMessageContent(new_clock)


def remove_clock_logic(clock_tag: str, executing_user: str) -> AbstractMessageContent:
    if type(executing_user) != str:
        logger.error(f"executing user is not a string")
        raise Exception("show_clock, executing_user is not a string for some reason")
    clock_tag = clean_clock_tag(clock_tag)
    clock_dic = load_clocks(executing_user)
    if clock_tag in clock_dic:
        del clock_dic[clock_tag]
        save_clocks(executing_user, clock_dic)
        return DictMessageContent(content="The clock has been deleted!\n", delay=MESSAGE_DELETION_DELAY)
    else:
        logger.error(
            f"The bot tried to remove a clock that does not exist for user: ({executing_user}), clock tag: ({clock_tag})")
        return DictMessageContent(content=f"Clock with this tag does not exist anymore: {clock_tag}")


def show_clock_command_logic(clock_tag: str, executing_user: str) -> AbstractMessageContent:
    if type(executing_user) != str:
        logger.error(f"executing user is not a string")
        raise Exception("show_clock, executing_user is not a string for some reason")
    clock_tag = clean_clock_tag(clock_tag)
    clock_dic = load_clocks(executing_user)
    if clock_tag in clock_dic:
        return ClockMessageContent(clock_dic[clock_tag])
    else:
        return DictMessageContent(content="This clock does not exist", delay=MESSAGE_DELETION_DELAY)


def tick_clock_logic(clock_tag: str, executing_user: str, ticks: int = 1) -> AbstractMessageContent:
    """
    Logic for accessing the clocks of the executing user and ticking a specific clock by the assigned ticks.
    Includes access checks

    :return: a AbstractMessageContent Object containing the paramaters that can be passed to a ContextInfo respond logic.
    """
    if type(executing_user) != str:
        logger.error(f"executing user is not a string")
        raise Exception("clock_tick, executing_user is not a string for some reason")
    clock_tag = clock_tag.strip().lower()
    clock_dic = load_clocks(executing_user)
    clock = clock_dic.get(clock_tag)
    if clock:
        clock.tick(ticks)
        save_clocks(executing_user, clock_dic)
        return ClockMessageContent(clock, executing_user)
    else:
        logger.error(
            f"The bot tried to tick a clock that does not exist for user: ({executing_user}), clock tag: ({clock_tag})"
        )
        return DictMessageContent(
            view=None,
            content=f"The clock with this tag: {clock_tag} was already deleted.\n",
            delay=MESSAGE_DELETION_DELAY
        )
