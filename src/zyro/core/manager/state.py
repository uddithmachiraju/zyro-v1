import hashlib
import json
import os
from datetime import datetime
from typing import Any, Callable

from zyro.core.logging import Logger


class StateManager(Logger):
    """Root-based state manager with versioning and migration support."""

    _STATE_FILENAME = ".zyro_state.json"
    _LOCK_FILENAME = ".zyro_state.json.lock"
    _CURRENT_VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self.state_data: dict[str, Any] = {}
        self._migrations: dict[int, Callable[[dict[str, Any]], None]] = {}
        self.logger.info("Initialized StateManager using root state file")

    def _get_timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _get_state_schema_hash(self) -> str:
        schema = {
            "version": self._CURRENT_VERSION,
            "fields": {
                k: type(v).__name__ for k, v in self.state_data.items()
            },
        }
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()[:16]

    def load_state(self) -> None:
        try:
            with open(self._STATE_FILENAME, "r", encoding="utf-8") as f:
                raw_state = json.load(f)

            state_version = raw_state.get("_meta", {}).get("version", 0)
            self.state_data = raw_state.get("data", {})

            if state_version < self._CURRENT_VERSION:
                self.logger.warning(
                    "State version mismatch. Current=%d, File=%d. Running migrations.",
                    self._CURRENT_VERSION,
                    state_version,
                )
                self._run_migrations(state_version, self._CURRENT_VERSION)
                self.save_state()
            else:
                self.logger.info(
                    "Loaded state (version %d)",
                    state_version,
                )

        except FileNotFoundError:
            self.logger.info("No state file found. Starting fresh.")
            self.state_data = {}

        except json.JSONDecodeError as e:
            self.logger.error("Invalid state file JSON: %s. Resetting state.", e)
            self.state_data = {}

    def save_state(self) -> None:
        state_with_meta = {
            "_meta": {
                "version": self._CURRENT_VERSION,
                "schema_hash": self._get_state_schema_hash(),
                "last_updated": self._get_timestamp(),
            },
            "data": self.state_data,
        }

        try:
            with open(self._STATE_FILENAME, "w", encoding="utf-8") as f:
                json.dump(state_with_meta, f, indent=4)
            self.logger.info("Saved state to %s", self._STATE_FILENAME)
        except Exception as e:
            self.logger.error("Failed to save state: %s", e)
            raise

    def add_state(self, key: str, value: Any) -> None:
        self.state_data[key] = value
        self.save_state()
        self.logger.debug("Set state: %s=%s", key, value)

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state_data.get(key, default)

    def remove_state(self, key: str) -> bool:
        if key in self.state_data:
            del self.state_data[key]
            self.save_state()
            self.logger.debug("Removed state: %s", key)
            return True
        return False

    def register_migration(
        self,
        version: int,
        migration_func: Callable[[dict[str, Any]], None],
    ) -> None:
        self._migrations[version] = migration_func

    def _run_migrations(self, from_version: int, to_version: int) -> None:
        for version in range(from_version + 1, to_version + 1):
            migration = self._migrations.get(version)
            if migration:
                self.logger.info("Running migration for version %d", version)
                migration(self.state_data)

    def lock_state(self, lock_id: str) -> bool:
        try:
            fd = os.open(
                self._LOCK_FILENAME,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
            os.write(
                fd,
                json.dumps(
                    {"lock_id": lock_id, "timestamp": self._get_timestamp()}
                ).encode(),
            )
            os.close(fd)
            self.logger.info("State locked by %s", lock_id)
            return True
        except FileExistsError:
            self.logger.warning("State already locked")
            return False

    def unlock_state(self) -> bool:
        try:
            os.remove(self._LOCK_FILENAME)
            self.logger.info("State lock released")
            return True
        except FileNotFoundError:
            return False

    def get_state_version(self) -> int:
        return self._CURRENT_VERSION
