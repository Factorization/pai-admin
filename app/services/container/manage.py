from datetime import datetime, timezone

import arrow
import docker

from .exceptions import InsufficientUptime, NotRunning


class Container:
    def __init__(self, name) -> None:
        self.name = name
        self.client = docker.from_env()

    @property
    def container(self):
        container = self.client.containers.get(self.name)
        container.reload()
        return container

    @property
    def status(self):
        try:
            return self.container.status.capitalize()
        except Exception:
            return "Unknown"

    @property
    def state(self):
        return self.client.api.inspect_container(self.container.id)["State"]

    @property
    def start_time(self):
        return datetime.fromisoformat(self.state["StartedAt"])

    @property
    def is_running(self):
        return self.state["Running"]

    @property
    def uptime(self):
        try:
            if self.is_running:
                now = datetime.now(timezone.utc)
                start_time = self.start_time
                uptime = now - start_time
                uptime_human_friendly = arrow.get(start_time).humanize(
                    only_distance=True
                )
                if uptime_human_friendly == "instantly":
                    uptime_human_friendly = "0 seconds"
                return uptime, uptime_human_friendly
            else:
                return "Unknown", "Unknown"
        except Exception:
            return "Unknown", "Unknown"

    def is_restartable(self, must_be_up_for_seconds=300):
        try:
            if not self.is_running:
                return False
            now = datetime.now(timezone.utc)
            if (now - self.start_time).seconds < int(must_be_up_for_seconds):
                return False
            return True
        except Exception:
            return False

    def restart(self, must_be_up_for_seconds=300):
        if self.is_running:
            if not self.is_restartable(must_be_up_for_seconds):
                raise InsufficientUptime(
                    f"Container {self.name}|{self.container.short_id} has not been running for {must_be_up_for_seconds} second(s)."
                )
            else:
                self.container.restart()
        else:
            raise NotRunning(
                f"Container {self.name}|{self.container.short_id} is not running."
            )
