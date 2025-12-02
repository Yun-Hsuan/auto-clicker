# 項目結構說明

## 推薦結構：frontend/backend

使用 `frontend/backend` 結構，即使使用直接函數調用，仍然可以保持清晰的代碼組織。

## 項目結構

```
AutoClicker/
├── frontend/              # GUI 前端
│   ├── views/            # GUI 視圖組件
│   │   └── main_window.py
│   ├── controllers/      # 控制器（連接 GUI 和後端）
│   │   └── example_controller.py
│   └── README.md
│
├── backend/              # 後端業務邏輯
│   ├── services/        # 服務類（業務邏輯）
│   │   └── example_service.py
│   └── models/          # 數據模型（可選）
│
├── main.py              # 程序入口
├── requirements.txt     # 依賴
└── README.md
```

## 架構說明

### 直接函數調用流程

```
main.py
  │
  ├──► frontend/views/main_window.py  (GUI 視圖)
  │           │
  │           └──► frontend/controllers/example_controller.py  (控制器)
  │                       │
  │                       └──► backend/services/example_service.py  (後端服務)
  │                                   │
  │                                   └──► 業務邏輯處理
```

### 關鍵特點

1. **清晰的職責分離**
   - `frontend/` - 所有 GUI 相關代碼
   - `backend/` - 所有業務邏輯代碼

2. **直接函數調用**
   - GUI → Controller → Service
   - 不需要 HTTP API
   - 所有代碼在同一個進程

3. **易於維護**
   - 結構清晰
   - 易於測試
   - 易於擴展

## 代碼示例

### 主程序入口

```python
# main.py
from PyQt5.QtWidgets import QApplication
from frontend.views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()  # GUI 內部會使用後端服務
    window.show()
    sys.exit(app.exec_())
```

### GUI 視圖

```python
# frontend/views/main_window.py
from frontend.controllers.example_controller import ExampleController

class MainWindow:
    def __init__(self):
        self.controller = ExampleController()  # 創建控制器
    
    def on_button_click(self):
        result = self.controller.handle_start_button_click(config)
```

### 控制器

```python
# frontend/controllers/example_controller.py
from backend.services.example_service import ExampleService

class ExampleController:
    def __init__(self):
        self.service = ExampleService()  # 直接創建服務實例
    
    def handle_start_button_click(self, config):
        return self.service.start_task(config)  # 直接調用
```

### 後端服務

```python
# backend/services/example_service.py
class ExampleService:
    def start_task(self, config):
        # 業務邏輯
        return {"status": "started"}
```

## 為什麼使用這種結構？

### ✅ 優點

1. **清晰的職責分離**
   - Frontend 負責 UI
   - Backend 負責業務邏輯
   - Controller 負責連接兩者

2. **易於理解**
   - 結構符合常見的 MVC 模式
   - 代碼組織清晰

3. **易於測試**
   - 可以單獨測試後端服務
   - 可以單獨測試控制器
   - 可以模擬測試 GUI

4. **易於擴展**
   - 未來如果需要進程分離，結構已經準備好
   - 可以輕鬆替換 GUI 框架

### ⚠️ 注意

- 雖然使用 `frontend/backend` 結構，但**不需要 HTTP API**
- 所有代碼在**同一個進程**中運行
- 使用**直接函數調用**，不是網絡通信

## 與 Web 應用的區別

| 特性 | Web 應用 | 桌面應用（本項目） |
|------|---------|------------------|
| 目錄結構 | frontend/backend | frontend/backend |
| 通信方式 | HTTP API | 直接函數調用 |
| 運行方式 | 兩個進程/服務 | 一個進程 |
| 部署方式 | 分別部署 | 打包成一個 .exe |

## 總結

使用 `frontend/backend` 結構是**完全可以的**，即使使用直接函數調用！

這種結構提供：
- ✅ 清晰的代碼組織
- ✅ 職責分離
- ✅ 易於維護
- ✅ 易於測試

關鍵是要理解：**結構是代碼組織方式，不是通信方式**。
即使使用直接函數調用，仍然可以使用清晰的目錄結構來組織代碼。

