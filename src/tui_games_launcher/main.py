import json
import subprocess
import os
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, Label, ListItem, ListView

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib # Fallback for older python (requires pip install tomli)

# Configuration path handling
DEFAULT_CONFIG_NAME = "games.toml"
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
SYSTEM_CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "tui-games-launcher")
SYSTEM_CONFIG_PATH = os.path.join(SYSTEM_CONFIG_DIR, DEFAULT_CONFIG_NAME)

# Use local file if it exists, otherwise use system config path
if os.path.exists(DEFAULT_CONFIG_NAME):
    CONFIG_FILE = DEFAULT_CONFIG_NAME
else:
    # Ensure directory exists for system config
    os.makedirs(SYSTEM_CONFIG_DIR, exist_ok=True)
    CONFIG_FILE = SYSTEM_CONFIG_PATH

class GameDetail(Static):
    """Displays details for the selected game."""
    
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("Select a game to see details", id="game-title")
            yield Label("", id="game-desc")
            yield Button("Launch", id="launch-btn", variant="primary", disabled=True)

    def update_game(self, game_data):
        self.query_one("#game-title").update(game_data.get("title", "Unknown"))
        self.query_one("#game-desc").update(game_data.get("description", "No description."))
        self.query_one("#launch-btn").disabled = False
        self.game_data = game_data

class GameLauncherApp(App):
    """A TUI Game Launcher built with Textual."""
    
    # Disable mouse support
    mouse_support = False

    ASCII_LOGO = r"""
  ____                         
 / ___| __ _ _ __ ___   ___ ___
| |  _ / _` | '_ ` _ \ / _ \/ __|
| |_| | (_| | | | | | |  __/\__ \
 \____|\__,_|_| |_| |_|\___||___/
    """

    CSS = """
    Screen {
        align: center middle;
        background: transparent;
    }

    #main-container {
        width: 60;
        height: 25;
        border: double ansi_white;
        padding: 1;
        background: transparent;
    }

    #logo {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: ansi_green;
        margin-bottom: 1;
    }

    #list-container {
        height: 10;
        border: solid ansi_white;
        margin-bottom: 1;
    }

    #details-container {
        height: 8;
        padding: 1;
        border: solid ansi_white;
    }

    #game-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        color: ansi_bright_white;
    }
    
    #game-desc {
        text-align: center;
        width: 100%;
        color: ansi_white;
    }
    
    #launch-btn {
        width: 100%;
        margin-top: 1;
        background: ansi_green;
        color: ansi_black;
        text-style: bold;
    }

    ListItem {
        padding: 0 1;
        background: transparent;
    }

    ListItem.--highlight {
        background: ansi_white 20%;
        text-style: bold reverse;
        color: ansi_bright_white;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("s", "scan_steam", "Scan Steam"),
        ("enter", "select_game", "Launch"),
    ]

    def __init__(self):
        super().__init__()
        self.games = self.load_games()
        self.selected_game = None

    def load_games(self):
        if not os.path.exists(CONFIG_FILE):
            return []
        try:
            with open(CONFIG_FILE, "rb") as f:
                data = tomllib.load(f)
                return data.get("games", [])
        except Exception:
            return []

    def save_games(self):
        """Save the current games list back to TOML."""
        import tomli_w  # We'll need this to write TOML
        try:
            with open(CONFIG_FILE, "wb") as f:
                tomli_w.dump({"games": self.games}, f)
        except ImportError:
            # If tomli_w isn't installed, we can't save easily
            # For now, let's just update the internal list
            pass

    def scan_steam_games(self):
        """Locates and parses Steam .acf files to find installed games."""
        steam_paths = [
            os.path.expanduser("~/.local/share/Steam/steamapps"),
            os.path.expanduser("~/.steam/steam/steamapps"),
            os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps"),
        ]
        
        found_games = []
        seen_ids = {g.get("id") for g in self.games}

        for path in steam_paths:
            if not os.path.exists(path):
                continue
            
            for file in os.listdir(path):
                if file.startswith("appmanifest_") and file.endswith(".acf"):
                    try:
                        with open(os.path.join(path, file), "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            # Basic manual parsing of ACF format
                            name = None
                            appid = None
                            for line in content.splitlines():
                                if '"name"' in line:
                                    name = line.split('"')[-2]
                                if '"appid"' in line:
                                    appid = line.split('"')[-2]
                            
                            if name and appid and appid not in seen_ids:
                                # Filter out common Steam non-game tools
                                name_lower = name.lower()
                                if any(tool in name_lower for tool in ["proton", "steam linux runtime", "steamworks", "steam controller"]):
                                    continue
                                    
                                found_games.append({
                                    "id": appid,
                                    "title": name,
                                    "command": f"steam steam://rungameid/{appid}",
                                    "description": f"Steam Game (AppID: {appid})"
                                })
                                seen_ids.add(appid)
                    except Exception:
                        continue
        return found_games

    def action_scan_steam(self):
        """Action triggered by 's' key."""
        new_games = self.scan_steam_games()
        if new_games:
            self.games.extend(new_games)
            # Refresh the UI
            self.recompose()
            # Try to save if possible
            try:
                import tomli_w
                with open(CONFIG_FILE, "wb") as f:
                    tomli_w.dump({"games": self.games}, f)
            except ImportError:
                pass

    def compose(self) -> ComposeResult:
        with Container(id="main-container"):
            yield Static(self.ASCII_LOGO, id="logo")
            
            with VerticalScroll(id="list-container"):
                items = [ListItem(Label(g["title"]), id=f"game-{i}") for i, g in enumerate(self.games)]
                yield ListView(*items, id="game-list")

            with Container(id="details-container"):
                yield GameDetail(id="game-detail")
        
        yield Footer()

    def on_mount(self):
        """Focus the list view automatically when starting."""
        self.query_one(ListView).focus()

    def action_cursor_down(self):
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self):
        self.query_one(ListView).action_cursor_up()

    def action_select_game(self):
        if self.selected_game:
            self.launch_game(self.selected_game)

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        """Update details when navigating the list."""
        if event.item:
            index = int(event.item.id.split("-")[1])
            self.selected_game = self.games[index]
            self.query_one(GameDetail).update_game(self.selected_game)

    def on_list_view_selected(self, event: ListView.Selected):
        """Handle Enter key when ListView is focused."""
        if self.selected_game:
            self.launch_game(self.selected_game)

    def launch_game(self, game):
        """Launches the selected game and exits the TUI."""
        command = game.get("command")
        if not command:
            return

        # Exit the TUI first so the terminal is clean
        self.exit(result=command)

def main():
    app = GameLauncherApp()
    # The app.run() will now return the command string when the app exits via self.exit(command)
    cmd = app.run()
    
    # Run the command after the TUI has fully closed
    if cmd:
        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(f"Error launching game: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
