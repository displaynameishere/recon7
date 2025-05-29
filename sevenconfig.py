import re
from typing import Union

class Config:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = {
            "targets": {},
            "secrets": {},
            "numbers": {},
            "theme": {}
        }
        self._parse_config()

    def _parse_config(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                if line.startswith("target:"):
                    self._parse_target(line)
                elif line.startswith("secret:"):
                    self._parse_secret(line)
                elif line.startswith("num:"):
                    self._parse_number(line)
                elif line.startswith("theme:"):
                    self._parse_theme(line)

    def _parse_target(self, line: str):
        match = re.match(r'target:(\w+)\s+"([^"]+)"(?:\s+"([^"]+)")?', line)
        if match:
            key, value, desc = match.groups()
            self.data["targets"][key] = {"value": value, "desc": desc or ""}

    def _parse_secret(self, line: str):
        match = re.match(r'secret:(\w+)\s+"([^"]+)"', line)
        if match:
            key, value = match.groups()
            self.data["secrets"][key] = value

    def _parse_number(self, line: str):
        match = re.match(r'num:(\w+)\s+(\d+)', line)
        if match:
            key, value = match.groups()
            self.data["numbers"][key] = int(value)

    def _parse_theme(self, line: str):
        match = re.match(r'theme:(\w+)\s+(#[0-9a-fA-F]{6})', line)
        if match:
            key, value = match.groups()
            self.data["theme"][key] = value

    # Accessor methods
    def get_target(self, key: str) -> Union[str, None]:
        return self.data["targets"].get(key, {}).get("value")

    def get_secret(self, key: str) -> Union[str, None]:
        return self.data["secrets"].get(key)

    def get_number(self, key: str) -> Union[int, None]:
        return self.data["numbers"].get(key)

    def get(self, key: str) -> Union[str, int, None]:
        """
        Allows access via 'theme:bg' or 'number:delay' style keys.
        """
        if ':' not in key:
            return None
        section, subkey = key.split(':', 1)
        return self.data.get(section, {}).get(subkey)

    def all_targets(self):
        return self.data["targets"]

    def all_secrets(self):
        return self.data["secrets"]

    def all_numbers(self):
        return self.data["numbers"]

    def all_theme(self):
        return self.data["theme"]
