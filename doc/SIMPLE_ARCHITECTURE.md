# 簡潔的架構說明（推薦方式）

## 核心原則

**對於同進程桌面應用：直接函數調用，不需要 Flask/FastAPI！**

## 完整的架構示例

### 1. 服務類（純 Python，無 HTTP）

```python
# backend/services/clicker_service.py
class ClickerService:
    """點擊服務類 - 純 Python，無 HTTP 依賴"""
    
    def __init__(self):
        self.is_running = False
        self.click_count = 0
    
    def start(self, config: dict) -> dict:
        """開始點擊"""
        self.is_running = True
        self.click_count = config.get('count', 0)
        return {"status": "started", "message": "點擊已開始"}
    
    def stop(self) -> dict:
        """停止點擊"""
        self.is_running = False
        return {"status": "stopped", "message": "點擊已停止"}
    
    def get_status(self) -> dict:
        """獲取狀態"""
        return {
            "is_running": self.is_running,
            "click_count": self.click_count
        }
```

### 2. GUI 使用服務（直接調用）

```python
# gui/views/main_window.py
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel
from backend.services.clicker_service import ClickerService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoClicker")
        
        # 直接創建服務實例（無 HTTP）
        self.service = ClickerService()
        
        # 創建 UI
        self.setup_ui()
    
    def setup_ui(self):
        # 開始按鈕
        self.start_btn = QPushButton("開始", self)
        self.start_btn.clicked.connect(self.on_start_clicked)
        
        # 停止按鈕
        self.stop_btn = QPushButton("停止", self)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        
        # 狀態標籤
        self.status_label = QLabel("未運行", self)
    
    def on_start_clicked(self):
        # 直接調用服務方法（無 HTTP！）
        config = {"count": 10, "interval": 1000}
        result = self.service.start(config)
        self.status_label.setText(result["message"])
    
    def on_stop_clicked(self):
        # 直接調用服務方法（無 HTTP！）
        result = self.service.stop()
        self.status_label.setText(result["message"])
```

### 3. 主程序入口

```python
# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 創建 GUI（GUI 內部會創建服務實例）
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

## 依賴清單（簡化）

```txt
# requirements.txt
pytest==7.4.3
pytest-cov==4.1.0
flake8==6.1.0

# 根據需要選擇 GUI 框架
PyQt5==5.15.10
# 或
# PySide6==6.6.0
# tkinter 是內置的，無需安裝

# ❌ 不需要 Flask
# ❌ 不需要 FastAPI
# ❌ 不需要 requests
# ❌ 不需要任何 HTTP 相關庫
```

## 為什麼不需要 Flask/FastAPI？

### Flask/FastAPI 的用途

- ✅ Web 應用（瀏覽器訪問）
- ✅ 遠程 API 服務
- ✅ 多客戶端同時訪問

### 桌面應用的特點

- ✅ 單一進程
- ✅ GUI 和後端在同一進程
- ✅ 直接函數調用即可
- ❌ 不需要網絡通信
- ❌ 不需要 HTTP 協議

## 對比

### 使用 Flask（不推薦用於同進程）

```python
# 後端
from flask import Flask
app = Flask(__name__)

@app.route('/api/start')
def start():
    return {"status": "started"}

# GUI
import requests
response = requests.get("http://127.0.0.1:5000/api/start")
```

**問題**：
- ❌ 需要啟動 HTTP 服務器
- ❌ 有網絡開銷
- ❌ 需要管理端口
- ❌ 增加複雜度

### 直接函數調用（推薦）

```python
# 後端服務類
class Service:
    def start(self):
        return {"status": "started"}

# GUI
service = Service()
result = service.start()  # 直接調用！
```

**優點**：
- ✅ 簡單直接
- ✅ 無開銷
- ✅ 易於調試
- ✅ 無額外依賴

## 項目結構

```
AutoClicker/
├── main.py                    # 程序入口
├── backend/
│   └── services/             # 服務類（純 Python）
│       └── clicker_service.py
├── gui/
│   └── views/                # GUI 視圖
│       └── main_window.py
└── requirements.txt          # 無 Flask/FastAPI！
```

## 總結

**對於您的桌面應用項目**：
- ✅ 使用**直接函數調用**
- ❌ **不需要** Flask/FastAPI
- ❌ **不需要** HTTP 協議
- ✅ **最簡單、最直接、最高效**

這就是桌面應用的最佳實踐！

