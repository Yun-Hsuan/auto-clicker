# 桌面應用 CI/CD 檢查指南

桌面應用開發**同樣需要 CI/CD**！以下是桌面應用特有的檢查項目。

## 桌面應用 CI/CD 檢查項目

### 1. 基礎檢查（與 Web 應用相同）

- ✅ **代碼格式檢查**（Lint）
- ✅ **單元測試**（Unit Tests）
- ✅ **代碼覆蓋率**（Code Coverage）
- ✅ **類型檢查**（Type Checking，如果使用類型提示）

### 2. 桌面應用特有檢查

#### 2.1 GUI 框架導入測試
確保 GUI 框架可以正常導入，不會因為缺少依賴而崩潰。

```python
# 測試 GUI 框架是否可以導入
def test_gui_imports():
    try:
        import PyQt5.QtWidgets  # 或 Tkinter
        assert True
    except ImportError:
        pytest.skip("GUI 框架未安裝")
```

#### 2.2 服務類實例化測試
測試後端服務類是否可以正常實例化（無需啟動 GUI）。

```python
def test_service_instantiation():
    from backend.services.example_service import ExampleService
    service = ExampleService()
    assert service is not None
```

#### 2.3 打包測試
測試應用是否可以成功打包為 .exe（在 Release 階段）。

#### 2.4 依賴完整性檢查
確保所有依賴都可以正常安裝，沒有版本衝突。

#### 2.5 GUI 組件初始化測試（可選）
測試 GUI 組件是否可以無頭模式初始化（不顯示窗口）。

## CI/CD 流程設計

### 開發階段（每次 Push/PR）

```
1. 代碼格式檢查 (flake8/black)
2. 類型檢查 (mypy, 可選)
3. 單元測試 (pytest)
4. 代碼覆蓋率報告
5. GUI 框架導入測試
6. 服務類功能測試
```

### 發布階段（Release/Tag）

```
1. 所有開發階段檢查
2. 打包測試 (PyInstaller)
3. 打包產物驗證
4. 創建 Release
5. 上傳構建產物
```

## 桌面應用 CI/CD 的特殊考量

### 1. 不需要 GUI 顯示器

CI 環境通常是無頭的（沒有顯示器），所以：

- ✅ **可以測試邏輯**：測試業務邏輯、服務類
- ✅ **可以測試導入**：確保 GUI 框架可以導入
- ⚠️ **不能顯示窗口**：無法進行真實的 UI 測試
- ✅ **可以使用無頭模式**：某些框架支持無頭測試

### 2. 打包驗證

- 測試 PyInstaller 是否可以成功打包
- 驗證打包後的 .exe 文件是否存在
- 檢查文件大小是否合理

### 3. 跨平台測試（可選）

- 如果支持多平台，在不同 OS 上測試
- Windows、Linux、macOS（如果適用）

## 實際檢查示例

### 檢查 1：代碼格式

```bash
# 使用 flake8
flake8 gui backend --max-line-length=120 --exclude=venv

# 或使用 black 格式化檢查
black --check gui backend
```

### 檢查 2：GUI 導入測試

```python
# tests/test_gui_imports.py
import pytest

def test_pyqt5_import():
    """測試 PyQt5 是否可以導入"""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        assert True
    except ImportError:
        pytest.skip("PyQt5 未安裝")

def test_gui_modules_import():
    """測試 GUI 模組是否可以導入"""
    try:
        from gui.views import main_window  # 根據實際結構調整
        assert True
    except ImportError as e:
        pytest.fail(f"GUI 模組導入失敗: {e}")
```

### 檢查 3：服務類功能測試

```python
# tests/test_services.py
from backend.services.example_service import ExampleService

def test_service_basic_functionality():
    """測試服務類基本功能"""
    service = ExampleService()
    
    # 測試初始化
    assert service is not None
    assert service.is_running == False
    
    # 測試方法
    status = service.get_status()
    assert status["status"] == "ok"
```

### 檢查 4：打包測試（Release 階段）

```yaml
# .github/workflows/release.yml
- name: Test PyInstaller build
  run: |
    pip install pyinstaller
    pyinstaller --onefile --windowed gui/main.py
    # 驗證 exe 文件是否存在
    Test-Path dist/main.exe
```

## 項目結構建議

```
AutoClicker/
├── tests/
│   ├── test_services.py        # 服務類測試
│   ├── test_gui_imports.py     # GUI 導入測試
│   └── test_integration.py     # 集成測試
├── .github/
│   └── workflows/
│       ├── ci.yml              # 持續集成
│       └── release.yml         # 發布流程
└── ...
```

## 與 Web 應用的區別

| 檢查項目 | Web 應用 | 桌面應用 |
|---------|---------|---------|
| 單元測試 | ✅ | ✅ |
| 代碼格式 | ✅ | ✅ |
| API 測試 | ✅ HTTP 端點 | ⚠️ 直接函數調用 |
| UI 測試 | ✅ Selenium | ⚠️ 困難（無頭環境） |
| 打包測試 | ✅ Docker 鏡像 | ✅ .exe 文件 |
| 部署測試 | ✅ 服務器部署 | ⚠️ 本地安裝測試 |

## 最佳實踐

1. **測試業務邏輯，而非 UI**
   - 重點測試服務類和業務邏輯
   - UI 測試在本地手動進行

2. **分層測試**
   - 單元測試：服務類
   - 集成測試：GUI + 服務（邏輯層面）
   - 手動測試：UI 交互

3. **打包驗證**
   - 在 Release 階段驗證打包
   - 檢查所有依賴都包含在打包中

4. **依賴管理**
   - 使用 `requirements.txt` 明確指定版本
   - CI 中測試依賴安裝

## 示例 CI 配置

查看 `.github/workflows/ci.yml` 了解完整的 CI 配置示例。

