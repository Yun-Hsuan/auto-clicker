# Orange Clicker - Backend 数据流分析文档

## 📋 目录结构

```
backend/
├── services/
│   ├── config_manager.py          # 配置文件管理（读取/保存 JSON）
│   ├── profile_service.py         # Profile 数据序列化/反序列化
│   ├── hotkey_service.py          # Hotkey 服务基类（共享 KeyboardListener）
│   ├── click_path_hotkey_service.py  # Click Path 录制热键（Ctrl+W, Ctrl+Q）
│   ├── profile_hotkey_service.py  # Profile 专用热键（Start/End 热键）
│   ├── cursor_clicker_service.py # 游标位置连续点击服务
│   └── click_path_executor_service.py  # Click Path 执行服务
└── utils/
    └── hotkey_converter.py        # 热键字符串格式转换
```

---

## 🔄 完整数据流分析

### 阶段 1: Config 文件读取

**触发点**: `MainWindow.on_card_active_changed()` (当 toggle switch 改变时)

```python
# 1. 从 ConfigManager 读取配置文件
config = self.config_manager.load_config()
profiles_data = config.get("profiles", [])

# 2. 使用 ProfileService 反序列化
for saved_profile_data in profiles_data:
    if saved_profile_data.get("id") == profile_id:
        saved_profile = ProfileService.deserialize_profile(saved_profile_data)
        profile.update(saved_profile)  # 更新内存中的 profile 数据
        profile["is_active"] = active  # 保持用户刚刚切换的状态
```

**关键模块**:
- `ConfigManager.load_config()`: 读取 `%APPDATA%\OrangeClicker\config.json`
- `ProfileService.deserialize_profile()`: 将 JSON 格式转换为应用格式
  - 判断 Profile 类型：`click_path` 有数据 = Click Path 模式，否则 = Cursor Position 模式
  - 提取所有字段：`id`, `name`, `start_hotkey`, `end_hotkey`, `is_active`, `is_saved`, `click_path`, `cursor_settings`

---

### 阶段 2: Hotkey 注册

**触发点**: `MainWindow.on_card_active_changed()` → `ProfileHotkeyService.register_profile_hotkeys(profile)`

```python
# ProfileHotkeyService.register_profile_hotkeys(profile)
# 1. 验证 profile 状态
if not profile.get("is_saved", False) or not profile.get("is_active", False):
    return  # 不注册

# 2. 存储 profile 数据到 _active_profile_hotkeys
self._active_profile_hotkeys[profile_id] = {
    "start_hotkey": start_hotkey,
    "end_hotkey": end_hotkey,
    "profile": profile  # 完整 profile 数据（包含 click_path）
}

# 3. 注册 hotkey 到 KeyboardListener
self.register_hotkey(start_hotkey, on_start_hotkey)  # 继承自 HotkeyService
```

**关键模块**:
- `HotkeyService.register_hotkey()`: 调用 `KeyboardListener.register_hotkey()`
- `KeyboardListener` (Singleton): 统一管理所有 hotkey，使用 `pynput.keyboard.GlobalHotKeys`
- `ProfileHotkeyService._active_profile_hotkeys`: 存储每个 profile 的 hotkey 信息和完整 profile 数据

**数据存储位置**:
```python
# ProfileHotkeyService._active_profile_hotkeys
{
    "profile_id_1": {
        "start_hotkey": "F10",
        "end_hotkey": "F9",
        "profile": {
            "id": "profile_id_1",
            "name": "Profile 1",
            "start_hotkey": "F10",
            "end_hotkey": "F9",
            "is_active": True,
            "is_saved": True,
            "click_path": [...],  # 如果有数据 = Click Path 模式
            "cursor_interval": 100,  # 如果 click_path 为空 = Cursor Position 模式
            "cursor_button": "left",
            "cursor_count": 0
        }
    }
}
```

---

### 阶段 3: Hotkey 触发

**触发点**: 用户按下 Start Hotkey (例如 F10)

```python
# KeyboardListener 检测到 hotkey 按下
# → 调用注册的 callback: on_start_hotkey()

# ProfileHotkeyService.on_start_hotkey() (闭包函数)
def on_start_hotkey():
    # STEP 1: 从 _active_profile_hotkeys 获取 profile 数据
    hotkey_info = self._active_profile_hotkeys.get(profile_id)
    stored_profile = hotkey_info.get("profile")
    
    # STEP 2: 验证 profile 状态
    if not stored_profile.get("is_active", False) or not stored_profile.get("is_saved", False):
        return
    
    # STEP 3: 判断 Profile 类型（关键决策点）
    click_path = stored_profile.get("click_path", [])
    
    if click_path and len(click_path) > 0:
        # Click Path 模式
        self._click_path_executor_service.start_execution(click_path)
    else:
        # Cursor Position 模式
        self._cursor_clicker_service.start_clicking(
            interval_ms=stored_profile.get("cursor_interval", 100),
            button=stored_profile.get("cursor_button", "left"),
            click_count=stored_profile.get("cursor_count", 0)
        )
```

**关键决策逻辑**:
- **判断条件**: `click_path and len(click_path) > 0`
  - `True` → Click Path 模式 → 调用 `ClickPathExecutorService`
  - `False` → Cursor Position 模式 → 调用 `CursorClickerService`

---

### 阶段 4A: Click Path 执行

**模块**: `ClickPathExecutorService`

```python
# ClickPathExecutorService.start_execution(click_path)
# click_path 格式:
[
    {
        "x": 100,
        "y": 200,
        "button": "left",
        "click_count": 1,
        "delay": 500,  # 毫秒，到下一个步骤的延迟
        "name": "Step 1"
    },
    {
        "x": 300,
        "y": 400,
        "button": "left",
        "click_count": 2,
        "delay": 1000,
        "name": "Step 2"
    }
]

# 执行流程（在独立线程中）:
for step in click_path:
    # 1. 移动游标到目标位置
    win32api.SetCursorPos((step["x"], step["y"]))
    
    # 2. 执行点击
    perform_native_click(step["x"], step["y"], step["button"], step["click_count"])
    
    # 3. 等待延迟（如果不是最后一步）
    if not last_step:
        time.sleep(step["delay"] / 1000.0)
```

**关键函数**:
- `perform_native_click()`: 在 `cursor_clicker_service.py` 中定义
  - 优先使用 `SendInput` API（游戏兼容性最好）
  - 回退到 `mouse_event` API
  - 最后回退到 `pynput`

---

### 阶段 4B: Cursor Position 连续点击

**模块**: `CursorClickerService`

```python
# CursorClickerService.start_clicking(interval_ms, button, click_count)
# 执行流程（在独立线程中）:
while self._is_clicking:
    # 1. 获取当前游标位置
    x, y = win32api.GetCursorPos()
    
    # 2. 在当前位置点击
    perform_native_click(x, y, button, times=1)
    
    # 3. 检查点击次数限制
    if click_count > 0 and current_count >= click_count:
        break  # 达到限制，停止
    
    # 4. 等待间隔时间
    time.sleep(interval_ms / 1000.0)
```

**关键参数**:
- `interval_ms`: 点击间隔（毫秒）
- `button`: 鼠标按钮（"left", "right", "middle"）
- `click_count`: 点击次数（0 = 无限）

---

## 🔍 关键数据流路径

### 路径 1: Config → Profile → Hotkey → Click Path 执行

```
ConfigManager.load_config()
    ↓
ProfileService.deserialize_profile()
    ↓
MainWindow.on_card_active_changed()
    ↓
ProfileHotkeyService.register_profile_hotkeys(profile)
    ↓ (存储到 _active_profile_hotkeys)
KeyboardListener.register_hotkey()
    ↓ (用户按下 Start Hotkey)
ProfileHotkeyService.on_start_hotkey()
    ↓ (判断: click_path 有数据)
ClickPathExecutorService.start_execution(click_path)
    ↓
perform_native_click() → SendInput API
```

### 路径 2: Config → Profile → Hotkey → Cursor Position 点击

```
ConfigManager.load_config()
    ↓
ProfileService.deserialize_profile()
    ↓
MainWindow.on_card_active_changed()
    ↓
ProfileHotkeyService.register_profile_hotkeys(profile)
    ↓ (存储到 _active_profile_hotkeys)
KeyboardListener.register_hotkey()
    ↓ (用户按下 Start Hotkey)
ProfileHotkeyService.on_start_hotkey()
    ↓ (判断: click_path 为空)
CursorClickerService.start_clicking(interval_ms, button, click_count)
    ↓
perform_native_click() → SendInput API
```

---

## 🎯 关键决策点

### 决策点 1: Profile 类型判断

**位置**: `ProfileHotkeyService.on_start_hotkey()` (line 169)

```python
click_path = stored_profile.get("click_path", [])

if click_path and len(click_path) > 0:
    # Click Path 模式
    self._click_path_executor_service.start_execution(click_path)
else:
    # Cursor Position 模式
    self._cursor_clicker_service.start_clicking(...)
```

**判断依据**:
- `click_path` 是列表且长度 > 0 → Click Path 模式
- `click_path` 为空或 None → Cursor Position 模式

### 决策点 2: Profile 是否可注册 Hotkey

**位置**: `ProfileHotkeyService.register_profile_hotkeys()` (line 81)

```python
if not profile.get("is_saved", False) or not profile.get("is_active", False):
    return  # 不注册
```

**条件**:
- `is_saved == True` AND `is_active == True` → 注册
- 否则 → 不注册

---

## 📊 数据存储位置

### 1. 配置文件
- **位置**: `%APPDATA%\OrangeClicker\config.json`
- **格式**: JSON
- **管理**: `ConfigManager`

### 2. 内存中的 Profile 数据
- **位置**: `MainWindow.profiles` (list)
- **格式**: Python dict
- **包含**: 所有 profile 数据 + `card` (UI 组件引用)

### 3. 已注册的 Hotkey 数据
- **位置**: `ProfileHotkeyService._active_profile_hotkeys` (dict)
- **格式**: `{profile_id: {"start_hotkey": str, "end_hotkey": str, "profile": dict}}`
- **用途**: Hotkey 触发时快速获取 profile 数据

### 4. KeyboardListener 的 Hotkey 注册
- **位置**: `KeyboardListener._hotkeys` (dict)
- **格式**: `{hotkey_string: callback_function}`
- **管理**: Singleton 模式，所有服务共享同一个实例

---

## 🔧 调试建议

### 1. 检查 Config 数据是否正确读取

```python
# 在 MainWindow.on_card_active_changed() 中添加日志
self._logger.info(f"📋 Profile data after reloading from config:")
self._logger.info(f"   - click_path type: {type(profile.get('click_path'))}")
self._logger.info(f"   - click_path length: {len(profile.get('click_path', []))}")
```

### 2. 检查 Hotkey 是否正确注册

```python
# 在 ProfileHotkeyService.register_profile_hotkeys() 中已有日志
logger.info(f"🔑 [Profile Hotkey] ✅ Stored profile data: click_path length={len(profile.get('click_path', []))}")
```

### 3. 检查 Hotkey 触发时的数据

```python
# 在 ProfileHotkeyService.on_start_hotkey() 中已有详细日志
logger.info(f"🎯 [Profile Hotkey] 📊 STEP 4: Checking click_path data")
logger.info(f"   - click_path type: {type(click_path)}")
logger.info(f"   - click_path length: {len(click_path) if click_path else 0}")
```

### 4. 检查执行服务是否正确调用

```python
# ClickPathExecutorService.start_execution() 中已有日志
logger.info(f"🛤️  [ClickPathExecutor] ⚡ start_execution called")
logger.info(f"   - click_path length: {len(click_path) if click_path else 'N/A'}")
```

---

## 🚨 常见问题排查

### 问题 1: Hotkey 不触发

**检查点**:
1. `ProfileHotkeyService._active_profile_hotkeys` 中是否有该 profile_id？
2. `KeyboardListener._hotkeys` 中是否有该 hotkey？
3. Profile 的 `is_saved` 和 `is_active` 是否为 `True`？

### 问题 2: 点击动作不执行

**检查点**:
1. `click_path` 数据是否正确传递到 `ClickPathExecutorService`？
2. `click_path` 格式是否正确（list of dict）？
3. `perform_native_click()` 是否成功调用？

### 问题 3: 执行了错误的模式

**检查点**:
1. `click_path` 是否为空？空 = Cursor Position，非空 = Click Path
2. Profile 数据是否正确从 config 读取？
3. `ProfileHotkeyService.on_start_hotkey()` 中的判断逻辑是否正确？

---

## 📝 总结

1. **数据读取**: `ConfigManager` → `ProfileService.deserialize_profile()` → 更新 `MainWindow.profiles`
2. **Hotkey 注册**: `ProfileHotkeyService.register_profile_hotkeys()` → 存储到 `_active_profile_hotkeys` → 注册到 `KeyboardListener`
3. **Hotkey 触发**: `KeyboardListener` 检测 → 调用 `on_start_hotkey()` callback
4. **模式判断**: 检查 `click_path` 是否有数据
5. **执行点击**: 
   - Click Path → `ClickPathExecutorService.start_execution()`
   - Cursor Position → `CursorClickerService.start_clicking()`

**关键**: 所有数据都从 `ProfileHotkeyService._active_profile_hotkeys[profile_id]["profile"]` 中获取，确保在注册 hotkey 时已经存储了最新的 profile 数据（包括从 config 重新加载的数据）。

