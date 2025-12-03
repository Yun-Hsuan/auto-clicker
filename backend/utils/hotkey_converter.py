"""
Hotkey Format Converter

Converts hotkey strings between different formats:
- UI format: "Ctrl+W", "F1", "Ctrl+Shift+A"
- pynput format: "<ctrl>+w", "<f1>", "<ctrl>+<shift>+a"
"""


def ui_to_pynput(ui_hotkey: str) -> str:
    """
    Convert UI hotkey format to pynput format.
    
    Args:
        ui_hotkey: Hotkey string in UI format (e.g., "Ctrl+W", "F1", "Ctrl+Shift+A")
    
    Returns:
        str: Hotkey string in pynput format (e.g., "<ctrl>+w", "<f1>", "<ctrl>+<shift>+a")
    """
    if not ui_hotkey or ui_hotkey == "#":
        return ""
    
    parts = ui_hotkey.split("+")
    pynput_parts = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        part_lower = part.lower()
        
        # Modifier keys
        if part_lower == "ctrl":
            pynput_parts.append("<ctrl>")
        elif part_lower == "alt":
            pynput_parts.append("<alt>")
        elif part_lower == "shift":
            pynput_parts.append("<shift>")
        elif part_lower == "meta":
            pynput_parts.append("<cmd>")  # Meta key on Mac, Windows key on Windows
        # Regular keys
        else:
            # Function keys
            if part_lower.startswith("f") and len(part_lower) > 1:
                try:
                    f_num = int(part_lower[1:])
                    if 1 <= f_num <= 12:
                        pynput_parts.append(f"<f{f_num}>")
                    else:
                        pynput_parts.append(part_lower)
                except ValueError:
                    pynput_parts.append(part_lower)
            # Special keys
            elif part_lower == "esc":
                pynput_parts.append("<esc>")
            elif part_lower == "enter":
                pynput_parts.append("<enter>")
            elif part_lower == "space":
                pynput_parts.append("<space>")
            elif part_lower == "tab":
                pynput_parts.append("<tab>")
            elif part_lower == "backspace":
                pynput_parts.append("<backspace>")
            elif part_lower == "delete":
                pynput_parts.append("<delete>")
            elif part_lower == "insert":
                pynput_parts.append("<insert>")
            elif part_lower == "home":
                pynput_parts.append("<home>")
            elif part_lower == "end":
                pynput_parts.append("<end>")
            elif part_lower == "pageup":
                pynput_parts.append("<page_up>")
            elif part_lower == "pagedown":
                pynput_parts.append("<page_down>")
            elif part_lower == "up":
                pynput_parts.append("<up>")
            elif part_lower == "down":
                pynput_parts.append("<down>")
            elif part_lower == "left":
                pynput_parts.append("<left>")
            elif part_lower == "right":
                pynput_parts.append("<right>")
            # Regular keys (letters, numbers)
            else:
                # For numbers, pynput expects them as strings (e.g., "2" not "<2>")
                # For letters, convert to lowercase
                pynput_parts.append(part_lower)
    
    result = "+".join(pynput_parts)
    return result


def ui_to_keyboard(ui_hotkey: str) -> str:
    """
    Convert UI hotkey format to keyboard library format.
    
    Args:
        ui_hotkey: Hotkey string in UI format (e.g., "Ctrl+W", "F1", "Ctrl+Shift+A")
    
    Returns:
        str: Hotkey string in keyboard library format (e.g., "ctrl+w", "f1", "ctrl+shift+a")
    """
    if not ui_hotkey or ui_hotkey == "#":
        return ""
    
    parts = ui_hotkey.split("+")
    keyboard_parts = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        part_lower = part.lower()
        
        # Modifier keys
        if part_lower == "ctrl":
            keyboard_parts.append("ctrl")
        elif part_lower == "alt":
            keyboard_parts.append("alt")
        elif part_lower == "shift":
            keyboard_parts.append("shift")
        elif part_lower == "meta":
            keyboard_parts.append("windows")  # Windows key
        # Regular keys
        else:
            # Function keys
            if part_lower.startswith("f") and len(part_lower) > 1:
                try:
                    f_num = int(part_lower[1:])
                    if 1 <= f_num <= 12:
                        keyboard_parts.append(f"f{f_num}")
                    else:
                        keyboard_parts.append(part_lower)
                except ValueError:
                    keyboard_parts.append(part_lower)
            # Special keys
            elif part_lower == "esc":
                keyboard_parts.append("esc")
            elif part_lower == "enter":
                keyboard_parts.append("enter")
            elif part_lower == "space":
                keyboard_parts.append("space")
            elif part_lower == "tab":
                keyboard_parts.append("tab")
            elif part_lower == "backspace":
                keyboard_parts.append("backspace")
            elif part_lower == "delete":
                keyboard_parts.append("delete")
            elif part_lower == "insert":
                keyboard_parts.append("insert")
            elif part_lower == "home":
                keyboard_parts.append("home")
            elif part_lower == "end":
                keyboard_parts.append("end")
            elif part_lower == "pageup":
                keyboard_parts.append("page up")
            elif part_lower == "pagedown":
                keyboard_parts.append("page down")
            elif part_lower == "up":
                keyboard_parts.append("up")
            elif part_lower == "down":
                keyboard_parts.append("down")
            elif part_lower == "left":
                keyboard_parts.append("left")
            elif part_lower == "right":
                keyboard_parts.append("right")
            # Regular keys (letters, numbers)
            else:
                keyboard_parts.append(part_lower)
    
    result = "+".join(keyboard_parts)
    return result

