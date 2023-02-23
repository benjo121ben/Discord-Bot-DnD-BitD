import logging
from threading import Timer
from typing import Any, Optional

logger = logging.getLogger('bot')


class TempEntry:
    def __init__(self, value: Any, time, func: callable):
        self.func = func
        self.value: Any = value
        self.time = time
        self.timer = Timer(time, func)
        self.timer.start()

    def reset_timer(self):
        self.timer.cancel()
        self.timer = Timer(self.time, self.func)
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def get(self):
        self.reset_timer()
        return self.value

    def set(self, value):
        self.reset_timer()
        self.value = value


class TempEntryDict:
    def __init__(self, deletion_time: int, entry_name: str):
        self.entry_name = entry_name
        self.deletion_time = deletion_time
        self.temp_entries: dict[str, TempEntry] = {}

    def remove(self, key: str):
        if key in self.temp_entries:
            self.temp_entries[key].cancel()
            del self.temp_entries[key]
            logger.info(f"{key}: {self.entry_name} was cleared from memory")

    def clear(self):
        while(len(self.temp_entries) > 0):
            key, val = self.temp_entries.popitem()
            val.cancel()

    def set(self, key, value):
        if key in self.temp_entries:
            self.temp_entries[key].set(value)
            logger.debug(f"{key}: {self.entry_name} timer was reset")
        else:
            self.temp_entries[key] = TempEntry(value, self.deletion_time, lambda: self.remove(key))

    def get(self, key) -> Optional[Any]:
        if key in self.temp_entries:
            logger.debug(f"{key}: {self.entry_name} timer was reset")
            return self.temp_entries[key].get()
        else:
            return None

    def __contains__(self, key: str) -> bool:
        return key in self.temp_entries

