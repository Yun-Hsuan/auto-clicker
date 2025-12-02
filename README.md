# Orange Clicker

A modern, cross‑platform desktop auto‑clicker built with **Python** and **PySide6**.

Orange Clicker is designed as a clean, extensible desktop app with a clear frontend/backend
separation, proper dependency management, multi‑language UI support, and a focus on
maintainability and future feature growth (click sequences, profiles, hotkeys, etc.).

---

## Features (Current & Planned)

**Current**
- Modern GUI built with **PySide6**
- Clear **frontend/backend** architecture
- Centralized **icon management** with multiple resolutions
- Centralized **font management** with Noto Sans TC & Roboto
- Simple **i18n system** based on JSON:
  - English (`en`)
  - Traditional Chinese (`zh-TW`)
- Runtime **language switching** via menu:
  - `Settings → Language → English`
  - `Settings → Language → Traditional Chinese`
- Basic example flow:
  - Click button → backend service returns a localized “Hello World” → UI shows message

**Planned / Ideas**
- Click sequence recording & playback
- Multiple profiles (per‑game / per‑task)
- Global hotkeys (start/stop)
- Advanced timing options (interval, randomization, duration)
- Configurable persistence (user config file)

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
│       └── clicker_service.py      # Backend business logic (example: Hello World)
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

You should see the **Orange Clicker** main window with:
- An icon in the window title bar
- A label and a button
- Menu bar with **Settings** and **Help**

Clicking the button will:
- Call the backend `ClickerService`
- Retrieve a localized “Hello World” message
- Show it in a message box and update the label

---

## Internationalization (i18n)

Orange Clicker uses a **simple JSON‑based i18n system**.

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
self.setWindowTitle(t("app.title", default="Orange Clicker"))
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

- Implement real clicker logic (mouse events, intervals, sequences)
- Add configuration UI:
  - Click interval, button, mode
  - Profiles (save/load to disk)
  - Hotkey configuration
- Persist user settings (e.g. JSON config in `backend/config/`)
- Add tests for backend services and i18n
- Package the app as a Windows `.exe` with a proper taskbar/start menu icon

---

## License

TBD – choose an appropriate open‑source license (e.g. MIT, Apache‑2.0) depending on
your intended usage and distribution model.
