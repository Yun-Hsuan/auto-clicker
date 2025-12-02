# 字體使用範例

本文檔展示如何使用已安裝的字體。

## 當前可用的字體

### Noto Sans TC (繁體中文)
- Regular, Bold, Medium, Light, SemiBold
- 路徑：`Noto_Sans_TC/static/`

### Roboto (英文)
- Regular, Bold, Medium, Light
- 路徑：`Roboto/static/`

## 使用方式

### 方式 1：使用預定義名稱（最簡單）

```python
from frontend.utils.font_manager import FontManager

# 獲取 Noto Sans TC Regular
font = FontManager.get_noto_tc_font('regular', point_size=12)
label.setFont(font)

# 獲取 Noto Sans TC Bold
bold_font = FontManager.get_noto_tc_font('bold', point_size=14)

# 獲取 Roboto Regular
roboto_font = FontManager.get_roboto_font('regular', point_size=11)
```

### 方式 2：使用完整路徑

```python
from frontend.utils.font_manager import FontManager

# 使用完整路徑
font = FontManager.create_font(
    font_filename="Noto_Sans_TC/static/NotoSansTC-Regular.ttf",
    point_size=12
)
label.setFont(font)
```

### 方式 3：在應用啟動時預加載（推薦）

在 `main.py` 中：

```python
from frontend.utils.font_manager import FontManager

# 預加載常用字體（使用預定義名稱）
FontManager.preload_fonts(
    'noto_tc_regular',
    'noto_tc_bold',
    'roboto_regular'
)

# 或使用完整路徑
FontManager.preload_fonts(
    'Noto_Sans_TC/static/NotoSansTC-Regular.ttf',
    'Roboto/static/Roboto-Regular.ttf'
)

# 設置為應用程序默認字體
default_font = FontManager.get_noto_tc_font('regular', point_size=10)
app.setFont(default_font)
```

### 方式 4：在組件中使用

```python
from frontend.utils.font_manager import FontManager

class MainWindow(QMainWindow):
    def init_ui(self):
        # 標題使用粗體
        title_font = FontManager.get_noto_tc_font('bold', point_size=16)
        title_label = QLabel("標題")
        title_label.setFont(title_font)
        
        # 正文使用常規字體
        body_font = FontManager.get_noto_tc_font('regular', point_size=12)
        body_label = QLabel("正文內容")
        body_label.setFont(body_font)
        
        # 按鈕使用中等字體
        button_font = FontManager.get_noto_tc_font('medium', point_size=11)
        button = QPushButton("按鈕")
        button.setFont(button_font)
```

## 預定義字體名稱列表

### Noto Sans TC
- `noto_tc_regular` - 常規
- `noto_tc_bold` - 粗體
- `noto_tc_medium` - 中等
- `noto_tc_light` - 細體
- `noto_tc_semibold` - 半粗體

### Roboto
- `roboto_regular` - 常規
- `roboto_bold` - 粗體
- `roboto_medium` - 中等
- `roboto_light` - 細體

## 完整範例

```python
# main.py
from frontend.utils.font_manager import FontManager

def main():
    app = QApplication(sys.argv)
    
    # 預加載字體
    FontManager.preload_fonts('noto_tc_regular', 'noto_tc_bold')
    
    # 設置默認字體
    app.setFont(FontManager.get_noto_tc_font('regular', point_size=10))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

```python
# main_window.py
from frontend.utils.font_manager import FontManager

class MainWindow(QMainWindow):
    def init_ui(self):
        # 使用 Noto Sans TC
        label = QLabel("繁體中文標籤")
        label.setFont(FontManager.get_noto_tc_font('regular', point_size=12))
        
        # 使用 Roboto（適合英文）
        english_label = QLabel("English Label")
        english_label.setFont(FontManager.get_roboto_font('regular', point_size=12))
```

## 注意事項

1. **字體加載**：建議在應用啟動時預加載，避免首次使用時的延遲
2. **字體選擇**：Noto Sans TC 適合中文，Roboto 適合英文
3. **混合使用**：可以為不同組件設置不同字體
4. **後備方案**：如果字體加載失敗，會自動使用系統默認字體


