# 🎮 TUI Games Launcher

A minimal, classic, keyboard-driven terminal game launcher built with Python and [Textual](https://textual.textualize.io/). Designed to be fast, theme-aware, and simple.

![Project Style](https://img.shields.io/badge/Style-Classic-lightgrey)
![Platform](https://img.shields.io/badge/Platform-Linux-blue)
![AUR](https://img.shields.io/badge/AUR-tui--games--launcher--git-brightgreen)

## ✨ Features

- **Classic & Minimalist**: No futuristic neon colors. It uses your terminal's natural color palette (ANSI colors) for a clean, consistent look.
- **Vim-Style Navigation**: Navigate your games using `j` and `k`, and launch them with `Enter`.
- **Steam Integration**: Automatically scan your Steam library (`s` key). It intelligently filters out Proton versions, runtimes, and other non-game tools.
- **Floating Window Ready**: Optimized for use in floating/popup terminal windows (like in Hyprland or Sway).
- **XDG Standards**: Saves your game list in `~/.config/tui-games-launcher/games.toml` for persistence across updates.
- **TOML Configuration**: Uses a human-readable TOML format that's easy to edit manually.

## 🚀 Installation

### Arch User Repository (AUR)
The easiest way to install on Arch Linux is via the AUR:
```bash
yay -S tui-games-launcher-git
```

### From Source
You can also install it manually as a Python package:
```bash
git clone https://github.com/Sombrechip88244/tui-games-launcher.git
cd tui-games-launcher
pip install .
```

## 🎮 Usage

Once installed, simply run:
```bash
gamest
```

### Keyboard Bindings
| Key | Action |
| :--- | :--- |
| `j` | Move selection down |
| `k` | Move selection up |
| `Enter` | Launch selected game and close TUI |
| `s` | Scan Steam library for new games |
| `q` | Quit the launcher |

## ⚙️ Configuration

The launcher stores its configuration in:
`~/.config/tui-games-launcher/games.toml`

### Example `games.toml`
```toml
[[games]]
id = "1"
title = "Super Tux Kart"
command = "supertuxkart"
description = "A 3D open-source kart racing game."

[[games]]
id = "413150"
title = "Stardew Valley"
command = "steam steam://rungameid/413150"
description = "Steam Game (AppID: 413150)"
```

## 🖥️ Hyprland Floating Window
To launch `gamest` in a centered floating window (using Ghostty or any other terminal), you can use this command in your Hyprland binds or Rofi shortcuts:

```bash
hyprctl dispatch exec "[float; size 900 600; center] ghostty --gtk-single-instance=false -e gamest"
```

## 🛠️ Development

If you want to contribute or modify the theme:
1. Install dependencies: `pip install -r requirements.txt`
2. Run locally: `python src/tui_games_launcher/main.py`

## 📄 License
This project is licensed under the MIT License.
