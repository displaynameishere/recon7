import re
import shutil
import os

class Config:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = {
            "secrets": {},
            "numbers": {},
            "theme": {}
        }
        self._load_config()

    def _load_config(self):
        try:
            self.data = {
                "secrets": {},
                "numbers": {},
                "theme": {}
            }
            with open(self.filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    if line.startswith("secret:"):
                        self._parse_secret(line)
                    elif line.startswith("num:"):
                        self._parse_number(line)
                    elif line.startswith("theme:"):
                        self._parse_theme(line)
        except FileNotFoundError:
            # no config, start empty
            pass
        except Exception as e:
            raise RuntimeError(f"Error loading config: {e}")

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

    # accessors
    def get_secret(self, key: str):
        return self.data["secrets"].get(key)

    def get_number(self, key: str):
        return self.data["numbers"].get(key)

    def get(self, key: str):
        """
        access 'theme:bg' or 'numbers:delay' style keys
        """
        if ':' not in key:
            return None
        section, subkey = key.split(':', 1)
        return self.data.get(section, {}).get(subkey)

    def all_secrets(self):
        return self.data["secrets"]

    def all_numbers(self):
        return self.data["numbers"]

    def all_theme(self):
        return self.data["theme"]

    def all(self):
        return self.data

    def save(self):
        # back^ current config before sav
        backup_path = self.filepath + ".save"
        try:
            if os.path.isfile(self.filepath):
                shutil.copyfile(self.filepath, backup_path)
        except Exception as e:
            raise RuntimeError(f"Error creating backup: {e}")

        # write current cfg
        try:
            with open(self.filepath, 'w') as f:
                for key, val in self.data["secrets"].items():
                    f.write(f'secret:{key} "{val}"\n')
                for key, val in self.data["numbers"].items():
                    f.write(f'num:{key} {val}\n')
                for key, val in self.data["theme"].items():
                    f.write(f'theme:{key} {val}\n')
        except Exception as e:
            raise RuntimeError(f"Error saving config: {e}")

    def reload(self):
        backup_path = self.filepath + ".save"
        try:
            self._load_config()
        except Exception:
            # if something breaks, try and load the backup
            try:
                self.filepath, backup_path = backup_path, self.filepath  # swap paths to load the backup
                self._load_config()
                self.save()  # save backup as current
            except Exception as e:
                raise RuntimeError(f"\033[0;31m ERR: Failed to reload config or backup: {e}")


class TargetLock:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.targets = {}  # key -> {"value": str, "desc": str}
        self._load_targets()

    def _load_targets(self):
        try:
            self.targets = {}
            with open(self.filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    match = re.match(r'(\w+)\s+"([^"]+)"(?:\s+"([^"]+)")?', line)
                    if match:
                        key, value, desc = match.groups()
                        self.targets[key] = {"value": value, "desc": desc or ""}
        except FileNotFoundError:
            self.targets = {}

    def all_targets(self):
        return self.targets

    def add_target(self, key: str, value: str, desc: str = ""):
        self.targets[key] = {"value": value, "desc": desc}
        self.save_targets()

    def delete_target(self, key: str):
        if key in self.targets:
            del self.targets[key]
            self.save_targets()

    def save_targets(self):
        # backup targets.lock before saving in case something breaks
        backup_path = self.filepath + ".save"
        try:
            if os.path.isfile(self.filepath):
                shutil.copyfile(self.filepath, backup_path)
        except Exception as e:
            raise RuntimeError(f"Error backing up targets: {e}")

        try:
            with open(self.filepath, 'w') as f:
                for key, target in self.targets.items():
                    val = target["value"]
                    desc = target["desc"]
                    if desc:
                        f.write(f'{key} "{val}" "{desc}"\n')
                    else:
                        f.write(f'{key} "{val}"\n')
        except Exception as e:
            raise RuntimeError(f"Error saving targets: {e}")

    def reload(self):
        self._load_targets()
