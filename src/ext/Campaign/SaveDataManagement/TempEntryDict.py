from threading import Timer
from typing import Any, Optional


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


class TempEntryDict:
    def __init__(self, deletion_time: int):
        self.deletion_time = deletion_time
        self.temp_entries: dict[str, TempEntry] = {}

    def clear_entry(self, key: str):
        if key in self.temp_entries:
            self.temp_entries[key].timer.cancel()
            del self.temp_entries[key]

    def set_value(self, key, value):
        if key in self.temp_entries:
            self.temp_entries[key].value = value
            self.temp_entries[key].reset_timer()
        else:
            self.temp_entries[key] = TempEntry(value, self.deletion_time, lambda: self.clear_entry(key))

    def get_value(self, key) -> Optional[Any]:
        if key in self.temp_entries:
            self.temp_entries[key].reset_timer()
            return self.temp_entries[key].value
        else:
            return None

    def __contains__(self, key: str) -> bool:
        return key in self.temp_entries

