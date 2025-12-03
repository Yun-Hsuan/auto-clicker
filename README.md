# Auto-Clicker

A modern, cross‑platform desktop auto‑clicker built with **Python** and **PySide6**.

Auto-Clicker is designed as a clean, extensible desktop app with a clear frontend/backend
separation, proper dependency management, multi‑language UI support, and a focus on
maintainability and future feature growth (click sequences, profiles, hotkeys, etc.).

---

## Features (Current & Planned)

**Current (Alpha)**
- **Modern GUI & architecture**
  - Built with **PySide6**
  - Clear separation between `frontend/` (Qt UI) and `backend/` (services)
  - Centralized **icon** / **font** / **theme** / **i18n** management
- **Profiles**
  - Multiple profiles (per‑game / per‑task)
  - Per‑profile **start / end hotkeys**
  - Toggle switch + status badge (`Setting`, `Active`, `Sleeping`)
- **Cursor Position mode**
  - Continuous clicking at current cursor position
  - Configurable interval, mouse button, and click count
  - Guard for **Infinite** click count (requires End hotkey)
- **Click Path mode**
  - Global hotkeys **Ctrl+W / Ctrl+Q** to start/stop recording
  - Native Windows mouse hook to record:
    - Click position
    - Button (left / right / middle)
    - Reaction time & listening method
  - Click sequence editor composed of `ClickStepItem` + `DelayTimer`
  - Execution engine replays `ClickStepItem → DelayTimer` in order
- **Global hotkeys (Win32 API)**
  - Unified keyboard listener built on `RegisterHotKey` with its own message loop thread
  - Uses native **SendInput** for clicks (with safe fallbacks)
- **Debugging & tooling**
  - **Debug Mode** toggle with live log panel
  - Extra controls like “Load Test Data” only visible in debug mode
- **UI / UX**
  - Tabs: **Cursor Position**, **Click Path**, **Visual Click (Coming Soon)**
  - Themed buttons (`Clear All` gray → blue on hover, etc.)
  - Goose‑themed dialogs for User Guide / About / Settings
- **Internationalization**
  - JSON‑based i18n:
    - English (`en`)
    - Traditional Chinese (`zh-TW`)
  - Runtime language switching via:
    - `Settings → Language → English`
    - `Settings → Language → Traditional Chinese`
- **Config & persistence**
  - Profiles stored in user config directory
  - Save flow that:
    - Forces you to choose **Cursor Position** *or* **Click Path**
    - Validates required fields and Infinite+End‑hotkey rules

**Planned / Ideas**
- Visual recognition click mode (`Visual Click` tab)
- More advanced timing options (randomization, duration, schedules)
- Better import/export of profiles and backup format
- Test coverage for backend services, hotkeys, and Win32 integration
- Windows packaging (`.exe`) with elevation and installer

---

## Tech Stack

- **Language**: Python 3.11+
- **GUI**: PySide6 (Qt for Python)
- **Architecture**:
  - `frontend/` – GUI, controllers, assets, i18n
  - `backend/` – business logic (clicker services)
- **Dependencies**: managed via `requirements.txt`
- **Environment**: recommended to use a **virtual environment** (`.venv`)

---

## Project Structure (High‑Level)

```text
auto-clicker/
├── backend/
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── cursor_clicker_service.py      # Core clicker using Win32 SendInput
│       ├── click_path_executor_service.py # Click path playback engine
│       ├── click_path_hotkey_service.py   # Ctrl+W / Ctrl+Q wiring
│       ├── profile_hotkey_service.py      # Per‑profile start/end hotkeys
│       ├── config_manager.py              # Load/save config & profiles
│       └── hotkey_service.py              # Shared hotkey utilities
│
├── frontend/
│   ├── __init__.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── clicker_controller.py   # Connects UI and backend service
│   ├── views/
│   │   ├── __init__.py
│   │   └── main_window.py          # Main window, menus, UI logic
│   ├── i18n/
│   │   ├── __init__.py
│   │   ├── en.json                 # English translations
│   │   ├── zh-TW.json              # Traditional Chinese translations
│   │   └── translation_manager.py  # JSON-based i18n manager
│   ├── public/
│   │   └── assets/
│   │       ├── icons/              # PNG icons in multiple sizes
│   │       ├── images/
│   │       └── fonts/              # Noto Sans TC, Roboto, docs
│   └── utils/
│       ├── __init__.py
│       ├── paths.py                # Resource path helpers
│       ├── icon_manager.py         # Icon loading & sizing
│       └── font_manager.py         # Font loading & helpers
│
├── doc/                            # Architecture & ops documentation
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
└── tests/                          # (Placeholder for future tests)
```

---

## Getting Started

### 1. Prerequisites

- **Python** 3.11+ installed
- Recommended: Git Bash or a terminal that supports Unix‑style commands on Windows

### 2. Create and Activate Virtual Environment

From the project root:

```bash
python -m venv .venv

# Git Bash / MINGW64
source .venv/Scripts/activate

# PowerShell (alternative)
# .\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` prefixed in your shell prompt after activation.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install **PySide6** and any other required packages.

### 4. Run the Application

From the project root, with the virtual environment activated:

```bash
py main.py
```

You should see the **Auto-Clicker** main window with:
- Left panel listing profiles (each with toggle switch and status badge)
- Right panel showing:
  - Status badge
  - Profile Name + Hotkey configuration row
  - Tabs for **Cursor Position**, **Click Path**, and **Visual Click (Coming Soon)**
  - Reset / Save buttons at the bottom

From there you can:
- Configure a profile (name, hotkeys, click mode)
- Record a click path with **Ctrl+W / Ctrl+Q**
- Start / stop auto‑clicking using your configured hotkeys

---

## Internationalization (i18n)

Auto-Clicker uses a **simple JSON‑based i18n system**.

- Language files:
  - `frontend/i18n/en.json`
  - `frontend/i18n/zh-TW.json`
- Manager:
  - `frontend/i18n/translation_manager.py`

Usage in code:

```python
from frontend.i18n.translation_manager import t, TranslationManager

# Set language at startup (main.py)
TranslationManager.set_language("en", fallback_lang="en")

# Translate in UI
self.setWindowTitle(t("app.title", default="Auto-Clicker"))
self.button.setText(t("main.button.click", default="Click Me"))
```

### Runtime Language Switching

You can switch UI language at runtime via:

- `Settings → Language → English`
- `Settings → Language → Traditional Chinese`

The main window updates:
- Window title
- Menus and submenu labels
- Main label text
- Button text
- Dialog titles

To add a new language:
1. Create `frontend/i18n/<lang>.json`
2. Add keys matching `en.json`
3. Wire it into the language menu and `TranslationManager.set_language("<lang>")`

---

## Icons & Fonts

### Icons

- Located in: `frontend/public/assets/icons/`
- Multiple PNG sizes (16×16, 32×32, 48×48, 64×64, 128×128, 256×256)
- Managed by `frontend/utils/icon_manager.py`

Example:

```python
from frontend.utils.icon_manager import IconManager

app_icon = IconManager.get_app_icon()  # 256x256, auto‑scaled by OS
window.setWindowIcon(app_icon)
```

### Fonts

- Located in: `frontend/public/assets/fonts/`
- Currently includes **Noto Sans TC** (for Traditional Chinese) and **Roboto**
- Managed by `frontend/utils/font_manager.py`

Example:

```python
from frontend.utils.font_manager import FontManager

# Preload fonts at startup (main.py)
FontManager.preload_fonts("noto_tc_regular", "roboto_regular")

# Set default app font
default_font = FontManager.get_noto_tc_font("regular", point_size=10)
app.setFont(default_font)

# Use font for a specific widget
label.setFont(FontManager.get_noto_tc_font("bold", point_size=14))
```

See `frontend/public/assets/fonts/README.md` and `USAGE_EXAMPLES.md` for more details.

---

## Development Notes

- Keep GUI logic in `frontend/views` and `frontend/controllers`
- Keep business logic in `backend/services`
- Add new user‑visible strings via i18n JSON instead of hard‑coding literals
- Prefer using:
  - `IconManager` for icons
  - `FontManager` for fonts
  - `TranslationManager` / `t()` for text

---

## Roadmap (High‑Level)

- Polish Click Path playback UX and error handling
- Implement Visual recognition click mode (`Visual Click` tab)
- Add more advanced scheduling/randomization options
- Improve configuration import/export and backup
- Add tests for backend services, hotkey layer, and i18n
- Package the app as a Windows `.exe` with proper elevation and Start Menu integration

---

## License

TBD – choose an appropriate open‑source license (e.g. MIT, Apache‑2.0) depending on
your intended usage and distribution model.
