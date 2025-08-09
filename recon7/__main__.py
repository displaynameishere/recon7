import curses
import recon7.sevenconfig as sevenconfig
import recon7.defaults as defaults
import os
import sys
import argparse

def parse_cli_args():
    default_config = os.path.expanduser("~/.config/recon7/config.7cfg")
    default_config_exists = os.path.isfile(default_config)

    parser = argparse.ArgumentParser(description="run recon7 with custom config path")

    parser.add_argument(
        "-c", "--config",
        required=False,
        help="path to the config file (optional, default: ~/.config/recon7/config.7cfg)"
    )

    args = parser.parse_args()

    if args.config:
        return args.config
    elif default_config_exists:
        return default_config
    else:
        if not os.path.exists(os.path.expanduser("~/.config/recon7")):
            os.makedirs(os.path.expanduser("~/.config/recon7"), exist_ok=True)
        with open(os.path.expanduser("~/.config/recon7/config.7cfg"), 'x') as f:
            f.write(defaults.DEFAULT_CONFIG)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return (1000, 1000, 1000)
    r = int(hex_str[0:2], 16) * 1000 // 255
    g = int(hex_str[2:4], 16) * 1000 // 255
    b = int(hex_str[4:6], 16) * 1000 // 255
    return (r, g, b)

class Recon7TUI:
    MIN_HEIGHT = 24
    MIN_WIDTH = 128

    def __init__(self, stdscr, config, targets_lock):
        self.stdscr = stdscr
        self.config = config
        self.targets_lock = targets_lock
        self.targets = list(self.targets_lock.all_targets().items())
        self.selected_index = 0
        self.message = ""

        self.theme = {
            'bg': self.config.get('theme:bg') or '#000000',
            'fg': self.config.get('theme:fg') or '#ffffff',
            'accent': self.config.get('theme:accent') or '#00ffff'
        }

    def check_terminal_size(self):
        h, w = self.stdscr.getmaxyx()
        if h < self.MIN_HEIGHT or w < self.MIN_WIDTH:
            self.stdscr.clear()
            warning_lines = [
                f"terminal size too small to run recon7 properly (w{w}xh{h})",
                f"please resize terminal to at least {self.MIN_WIDTH}x{self.MIN_HEIGHT}",
                "recon7 will automatically start when resized after you press [enter]"
            ]
            for i, line in enumerate(warning_lines):
                self.stdscr.addstr(i, 0, line)
            self.stdscr.refresh()
            while True:
                key = self.stdscr.getch()
                if key in (curses.KEY_ENTER, 10, 13):
                    h, w = self.stdscr.getmaxyx()
                    if h >= self.MIN_HEIGHT and w >= self.MIN_WIDTH:
                        break
                elif key == ord('q'):
                    sys.exit(1)

    def init_colors(self):
        curses.start_color()
        if curses.can_change_color():
            curses.use_default_colors()
            curses.init_color(10, *hex_to_rgb(self.theme['bg']))
            curses.init_color(11, *hex_to_rgb(self.theme['fg']))
            curses.init_color(12, *hex_to_rgb(self.theme['accent']))
            curses.init_pair(1, 11, 10)
            curses.init_pair(2, 10, 11)
            curses.init_pair(3, 12, 10)
        else:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    def draw(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        for y in range(h):
            self.stdscr.addstr(y, 0, " " * (w - 1), curses.color_pair(1))
        title = "recon7: targets"
        self.stdscr.addstr(0, 0, title[:w], curses.color_pair(1))
        for idx, (key, info) in enumerate(self.targets):
            line = f"{key}: {info['value']}  "
            if idx == self.selected_index:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(idx + 2, 0, line[:w])
                self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.addstr(idx + 2, 0, line[:w], curses.color_pair(1))
            desc_x = len(line)
            desc_text = info.get('desc', '')
            if desc_text:
                self.stdscr.addstr(idx + 2, desc_x, desc_text[:w - desc_x], curses.color_pair(3))
        if self.message:
            self.stdscr.addstr(h - 2, 0, self.message[:w], curses.A_BOLD | curses.color_pair(3))
        help_line = "a=Add  d=Delete  Enter=Select  r=Reload Config q=Quit"
        self.stdscr.addstr(h - 1, 0, help_line[:w], curses.A_DIM | curses.color_pair(1))
        self.stdscr.refresh()

    def select_target_type(self):
        types = ["IP target", "Domain target", "URL target"]
        selected = 0
        h, w = self.stdscr.getmaxyx()
        win_height = len(types) + 2
        win_width = 24
        win_y = h // 2 - win_height // 2
        win_x = w // 2 - win_width // 2
        win = curses.newwin(win_height, win_width, win_y, win_x)
        win.keypad(True)
        curses.curs_set(0)
        while True:
            win.clear()
            win.box()
            win.addstr(0, 2, "Select Target Type", curses.color_pair(1))
            for i, t in enumerate(types):
                if i == selected:
                    win.attron(curses.color_pair(2))
                    win.addstr(i + 1, 2, t)
                    win.attroff(curses.color_pair(2))
                else:
                    win.addstr(i + 1, 2, t, curses.color_pair(1))
            win.refresh()
            key = win.getch()
            if key in (curses.KEY_UP, ord('k')):
                selected = (selected - 1) % len(types)
            elif key in (curses.KEY_DOWN, ord('j')):
                selected = (selected + 1) % len(types)
            elif key in (curses.KEY_ENTER, 10, 13):
                curses.curs_set(1)
                return types[selected].split()[0].lower()
            elif key == 27:
                curses.curs_set(1)
                return None

    def add_target(self):
        target_type = self.select_target_type()
        if target_type is None:
            self.message = "Add cancelled."
            return
        prompt_map = {
            "ip": "Enter key and IP (with optional desc in brackets):",
            "domain": "Enter key and domain [desc]:",
            "url": "Enter key and URL [desc]:"
        }
        example_map = {
            "ip": "Example: target1 192.168.1.1 Internal LAN",
            "domain": "Example: mysite example.com Example site",
            "url": "Example: scan1 http://example.com Landing page"
        }
        prompt = prompt_map.get(target_type, "Enter key and value [desc]:")
        example = example_map.get(target_type, "")
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, prompt, curses.color_pair(1))
        self.stdscr.addstr(1, 0, example, curses.color_pair(3))
        self.stdscr.refresh()
        curses.echo()
        inp = self.stdscr.getstr(2, 0, 100).decode().strip()
        curses.noecho()
        if not inp:
            self.message = "Add cancelled."
            return
        parts = inp.split(maxsplit=2)
        if len(parts) < 2:
            self.message = "Error: Need at least key and value."
            return
        key, value = parts[0], parts[1]
        desc = parts[2] if len(parts) == 3 else ""
        self.targets_lock.add_target(key, value, desc)
        self.targets = list(self.targets_lock.all_targets().items())
        self.selected_index = len(self.targets) - 1
        self.message = f"Added target '{key}'."


    def delete_target(self):
        if not self.targets:
            self.message = "No targets to delete."
            return
        key, _ = self.targets[self.selected_index]
        self.targets_lock.delete_target(key)
        self.targets = list(self.targets_lock.all_targets().items())
        self.selected_index = min(self.selected_index, len(self.targets) - 1)
        self.message = f"Deleted target '{key}'."

    def select_target(self):
        if not self.targets:
            self.message = "No targets to select."
            return
        key, info = self.targets[self.selected_index]
        self.message = f"Selected target: {key} -> {info['value']}"

    def reload_all(self):
        try:
            self.config.reload()
            self.targets_lock.reload()
            self.targets = list(self.targets_lock.all_targets().items())
            self.theme = {
                'bg': self.config.get('theme:bg') or '#000000',
                'fg': self.config.get('theme:fg') or '#ffffff',
                'accent': self.config.get('theme:accent') or '#00ffff'
            }
            self.init_colors()
            self.message = "Config and targets reloaded."
        except Exception as e:
            self.message = f"Reload error: {e}"

    def run(self):
        curses.curs_set(0)
        self.init_colors()
        self.check_terminal_size()
        while True:
            self.draw()
            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord('k')):
                self.selected_index = max(0, self.selected_index - 1)
            elif key in (curses.KEY_DOWN, ord('j')):
                self.selected_index = min(len(self.targets) - 1, self.selected_index + 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                self.select_target()
            elif key == ord('a'):
                self.add_target()
            elif key == ord('d'):
                self.delete_target()
            elif key == ord('r'):
                self.reload_all()
            elif key == ord('q'):
                break
            else:
                self.message = "Use a/d/↑↓/Enter/r/q"

if __name__ == "__main__":
    config_path = parse_cli_args()
    targets_path = os.path.expanduser("~/.config/recon7/targets.lock")
    if config_path:
        if not os.path.isfile(config_path):
            print(f"\033[0;31mERR: config file not found at {config_path}\033[0m")
            sys.exit(1)
    config = sevenconfig.Config(config_path)
    targets = sevenconfig.TargetLock(targets_path)
    curses.wrapper(lambda stdscr: Recon7TUI(stdscr, config, targets).run())
