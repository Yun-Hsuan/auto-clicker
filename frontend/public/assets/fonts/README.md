# 字體文件說明

此目錄存放應用程序使用的自定義字體文件。

## 支援的字體格式

- `.ttf` (TrueType Font) - 推薦
- `.otf` (OpenType Font)
- `.ttc` (TrueType Collection)

## 使用方式

### 1. 添加字體文件

將字體文件（如 `Roboto-Regular.ttf`）放入此目錄。

### 2. 在代碼中使用

#### 方式 1：在應用啟動時預加載（推薦）

在 `main.py` 中：

```python
from frontend.utils.font_manager import FontManager

# 預加載字體
FontManager.preload_fonts("Roboto-Regular.ttf", "Roboto-Bold.ttf")

# 設置為應用程序默認字體
default_font = FontManager.create_font(font_filename="Roboto-Regular.ttf", point_size=10)
app.setFont(default_font)
```

#### 方式 2：在特定組件中使用

```python
from frontend.utils.font_manager import FontManager

# 創建字體對象
custom_font = FontManager.create_font(
    font_filename="Roboto-Regular.ttf",
    point_size=12,
    weight=QFont.Weight.Normal
)

# 應用到組件
label.setFont(custom_font)
button.setFont(custom_font)
```

#### 方式 3：直接使用字體族名

```python
from frontend.utils.font_manager import FontManager

# 先加載字體獲取族名
font_family = FontManager.get_font_family("Roboto-Regular.ttf")

# 然後創建字體
font = FontManager.create_font(
    font_family=font_family,
    point_size=12
)
```

## 字體權重

可以使用以下權重值：

```python
from PySide6.QtGui import QFont

QFont.Weight.Thin          # 100
QFont.Weight.ExtraLight    # 200
QFont.Weight.Light         # 300
QFont.Weight.Normal        # 400
QFont.Weight.Medium        # 500
QFont.Weight.DemiBold      # 600
QFont.Weight.Bold          # 700
QFont.Weight.ExtraBold     # 800
QFont.Weight.Black         # 900
```

## 推薦字體

### 中文字體推薦（免費開源）

1. **Noto Sans CJK / Noto Sans SC** ⭐ 最推薦
   - Google 設計，專為中文優化
   - 支援簡體中文、繁體中文、日文、韓文
   - 字體清晰，易讀性極佳
   - 下載：https://fonts.google.com/noto/specimen/Noto+Sans+SC
   - 或：https://github.com/googlefonts/noto-cjk

2. **思源黑體 (Source Han Sans)** ⭐ 推薦
   - Adobe 與 Google 合作開發
   - 支援簡繁中文，字體優美
   - 多種字重（Regular, Bold 等）
   - 下載：https://github.com/adobe-fonts/source-han-sans
   - 簡體：SourceHanSansSC-Regular.otf
   - 繁體：SourceHanSansTC-Regular.otf

3. **思源宋體 (Source Han Serif)**
   - 適合需要正式感的應用
   - 下載：https://github.com/adobe-fonts/source-han-serif

4. **文泉驛字體 (WenQuanYi)**
   - 開源中文字體，輕量級
   - 下載：http://wenq.org/wqy2/

5. **站酷字體系列**
   - 站酷高端黑、站酷快樂體等
   - 適合創意類應用
   - 下載：https://www.zcool.com.cn/special/zcoolfonts/

### 英文/通用字體推薦（免費開源）

1. **Roboto** - Google 設計，現代簡潔
   - 下載：https://fonts.google.com/specimen/Roboto

2. **Inter** - 專為屏幕設計
   - 下載：https://rsms.me/inter/

3. **Noto Sans** - Google 設計，支援多語言
   - 下載：https://fonts.google.com/noto/specimen/Noto+Sans

4. **Open Sans** - 易讀性高
   - 下載：https://fonts.google.com/specimen/Open+Sans

5. **Source Sans Pro** - Adobe 設計
   - 下載：https://fonts.google.com/specimen/Source+Sans+Pro

### 中英文混合使用建議

**推薦組合：**
- **Noto Sans SC** (中文) + **Roboto** (英文) - 風格統一
- **思源黑體** (中文) + **Source Sans Pro** (英文) - 同源設計
- **Noto Sans SC** (中文) + **Noto Sans** (英文) - 完美搭配

**使用方式：**
```python
# 優先使用中文字體，英文會自動回退到英文字體
chinese_font = FontManager.create_font(font_filename="NotoSansSC-Regular.ttf", point_size=12)
label.setFont(chinese_font)
```

## 注意事項

1. **字體授權**：確保使用的字體有適當的授權（商業使用需要檢查授權）
2. **文件大小**：字體文件可能較大，考慮應用程序大小
3. **加載時機**：建議在應用啟動時預加載，避免首次使用時的延遲
4. **後備方案**：如果字體加載失敗，會自動使用系統默認字體

## 示例

完整的使用示例請參考：
- `main.py` - 應用啟動時的預加載
- `frontend/views/main_window.py` - 組件中的使用示例

