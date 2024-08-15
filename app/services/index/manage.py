from datetime import datetime, timezone
from pathlib import Path

import arrow


class IndexFile:
    def __init__(self, running_file_path, complete_file_path) -> None:
        self.running_file = Path(running_file_path)
        self.complete_file = Path(complete_file_path)

    def delete_index_complete_flag(self):
        self.complete_file.unlink(missing_ok=True)
        return

    @staticmethod
    def index_flag_status(file):
        if file.exists():
            stats = file.stat()
            created_at = datetime.fromtimestamp(stats.st_ctime, tz=timezone.utc)
            return created_at, arrow.get(created_at).humanize()
        else:
            return "Unknown", "Unknown"

    def running_status(self):
        return self.index_flag_status(self.running_file)

    def complete_status(self):
        return self.index_flag_status(self.complete_file)

    def is_running(self):
        return self.running_file.exists()

    def is_complete(self):
        return self.complete_file.exists()

    def is_restartable(self, must_be_up_for_seconds=300):
        if self.is_running() is False and self.is_complete() is True:
            created_at = self.complete_status()[0]
            now = datetime.now(timezone.utc)
            if type(created_at) is datetime:
                if (now - created_at).seconds >= int(must_be_up_for_seconds):
                    return True
        return False
