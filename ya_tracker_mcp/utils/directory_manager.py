import os
import time
import yaml
from datetime import datetime

# Path to the directories configuration and data — shared across all sessions
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "ya-tracker-mcp")
CONFIG_PATH = os.path.join(CACHE_DIR, "directories.yaml")

DEFAULT_TTLS = {
    "issue_types": 86400,    # 24h
    "statuses": 86400,       # 24h
    "priorities": 86400,     # 24h
    "resolutions": 86400,    # 24h
    "global_fields": 86400,  # 24h
    "field_categories": 86400, # 24h
    "queues": 3600,          # 1h
    "components": 3600,      # 1h
    "boards": 3600,          # 1h
    "sprints": 1800,         # 30m
    "users": 3600,           # 1h
    "queue_fields": 1800,    # 30m
    "queue_tags": 900,       # 15m
}

class DirectoryManager:
    def __init__(self):
        self._load()

    def _load(self):
        if not os.path.exists(CONFIG_PATH):
            self.data = {}
            self.config = {"ttls": DEFAULT_TTLS.copy()}
            return

        try:
            with open(CONFIG_PATH, "r") as f:
                full_data = yaml.safe_load(f) or {}
                self.data = full_data.get("data", {})
                self.config = full_data.get("config", {"ttls": DEFAULT_TTLS.copy()})
                if "ttls" not in self.config:
                    self.config["ttls"] = DEFAULT_TTLS.copy()
        except Exception:
            self.data = {}
            self.config = {"ttls": DEFAULT_TTLS.copy()}

    def _save(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        try:
            with open(CONFIG_PATH, "w") as f:
                yaml.dump({
                    "config": self.config,
                    "data": self.data,
                    "meta": {
                        "last_saved": datetime.now().isoformat()
                    }
                }, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"Error saving directory cache: {e}")

    def get_ttl(self, directory: str) -> int:
        return self.config["ttls"].get(directory, DEFAULT_TTLS.get(directory, 3600))

    def set_ttl(self, directory: str, ttl: int):
        self.config["ttls"][directory] = ttl
        self._save()

    def _get_cache_key(self, directory: str, scope: str | None = None) -> str:
        return f"{directory}:{scope}" if scope else directory

    async def get(self, directory: str, fetch_func, scope: str | None = None, force: bool = False):
        key = self._get_cache_key(directory, scope)
        entry = self.data.get(key)
        now = time.time()
        ttl = self.get_ttl(directory)

        if not force and entry and (now - entry.get("timestamp", 0) < ttl):
            return entry.get("values")

        # Fetch from API
        values = await fetch_func()
        
        # Save to cache
        self.data[key] = {
            "values": values,
            "timestamp": now,
            "updated_at": datetime.now().isoformat()
        }
        self._save()
        return values

    def get_status(self):
        status = []
        now = time.time()
        for key, entry in self.data.items():
            ts = entry.get("timestamp", 0)
            dir_type = key.split(":")[0]
            ttl = self.get_ttl(dir_type)
            expires_in = max(0, int(ts + ttl - now))
            
            status.append({
                "key": key,
                "count": len(entry.get("values", [])),
                "updated_at": entry.get("updated_at"),
                "ttl": ttl,
                "expires_in_sec": expires_in,
                "is_expired": expires_in == 0
            })
        return status

    async def sync_all(self, registry: dict):
        """
        Sync all directories using a registry of fetch functions.
        registry: { "directory_name": fetch_func, "directory_name:scope": fetch_func }
        """
        results = []
        for key, fetch_func in registry.items():
            parts = key.split(":", 1)
            directory = parts[0]
            scope = parts[1] if len(parts) > 1 else None
            try:
                await self.get(directory, fetch_func, scope=scope, force=True)
                results.append(f"✅ {key} synced")
            except Exception as e:
                results.append(f"❌ {key} failed: {str(e)}")
        return results

# Singleton instance
manager = DirectoryManager()
