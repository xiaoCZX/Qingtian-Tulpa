# 音频频谱图SVG生成器 🎵

一个功能强大的 Python 工具，用于分析音频文件并生成可定制的 SVG 频谱图。

## ✨ 特性

- 📁 **多格式支持**: 支持 WAV, MP3, OGG, FLAC, M4A 等常见音频格式
- 🎨 **高度可定制**: 通过 TOML 配置文件轻松调整所有参数
- 🎯 **全频段分析**: 支持自定义频率范围（默认 20Hz - 20kHz）
- 📏 **自适应长度**: 音频时间越长，生成的频谱条越多
- 🎭 **灵活对齐**: 支持频谱条居中、居上、居下对齐
- 🌈 **纯色样式**: 可自定义颜色和圆角，符合现代设计美学
- ⚡ **快速高效**: 基于 librosa 和 numpy 的高性能音频处理

## 📦 安装依赖

```bash
pip install numpy librosa tomli
```

### 依赖说明

- `numpy`: 数值计算和数组处理
- `librosa`: 音频分析和处理库
- `tomli`: TOML 配置文件解析（Python 3.11+ 内置 tomllib）

如果需要处理 MP3 格式，可能还需要安装 ffmpeg：

```bash
# Windows (使用 Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

## 🚀 快速开始

### 1. 基本使用

```bash
# 使用默认配置文件 (config.toml)
python audio_spectrum_svg.py

# 使用自定义配置文件
python audio_spectrum_svg.py -c my_config.toml

# 直接指定输入输出文件（覆盖配置文件设置）
python audio_spectrum_svg.py -i audio.mp3 -o spectrum.svg

# 组合使用
python audio_spectrum_svg.py -c example_config.toml -i my_audio.wav -o my_spectrum.svg
```

### 2. 配置文件示例

创建一个 `config.toml` 文件：

```toml
[audio]
input_file = "your_audio.mp3"
output_file = "spectrum.svg"

[spectrum]
time_window = 0.05          # 时间窗口大小（秒）
freq_min = 20               # 最小频率（Hz）
freq_max = 20000            # 最大频率（Hz）
num_bars = 0                # 0=自动计算
bars_per_second = 10        # 每秒生成的频谱条数

[svg]
width = 0                   # 0=自动计算
height = 150                # SVG高度
bar_width = 6               # 频谱条宽度
bar_spacing = 7             # 频谱条间距
bar_color = "#000000"       # 颜色（十六进制）
border_radius = 2           # 圆角半径
min_bar_height = 15         # 最小高度
max_bar_height_percent = 95 # 最大高度百分比
background_color = ""       # 背景色（留空=透明）

[alignment]
vertical_align = "center"   # center/top/bottom
```

## ⚙️ 配置参数详解

### 🎵 音频配置 `[audio]`

| 参数 | 说明 | 示例 |
|------|------|------|
| `input_file` | 输入音频文件路径 | `"audio.mp3"` |
| `output_file` | 输出SVG文件路径 | `"spectrum.svg"` |

### 📊 频谱配置 `[spectrum]`

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `time_window` | 分析时间窗口大小（秒） | `0.05` - `0.1` |
| `freq_min` | 最小分析频率（Hz） | `20` |
| `freq_max` | 最大分析频率（Hz） | `20000` |
| `num_bars` | 频谱条数量（0=自动） | `0` |
| `bars_per_second` | 每秒生成的频谱条数 | `8` - `15` |

**频谱条数量建议：**
- 短音频（<5秒）: `bars_per_second = 12-15`
- 中等音频（5-30秒）: `bars_per_second = 8-12`
- 长音频（>30秒）: `bars_per_second = 5-8`

### 🎨 SVG样式配置 `[svg]`

| 参数 | 说明 | 示例 |
|------|------|------|
| `width` | SVG宽度（0=自动计算） | `0` 或 `800` |
| `height` | SVG高度 | `150` - `200` |
| `bar_width` | 频谱条宽度（像素） | `4` - `8` |
| `bar_spacing` | 频谱条间距（像素） | `5` - `10` |
| `bar_color` | 颜色（十六进制） | `"#000000"`, `"#FF5733"` |
| `border_radius` | 圆角半径 | `0` - `5` |
| `min_bar_height` | 最小条高度 | `10` - `20` |
| `max_bar_height_percent` | 最大高度百分比 | `90` - `100` |
| `background_color` | 背景色（空=透明） | `""` 或 `"#FFFFFF"` |

**颜色预设示例：**
```toml
bar_color = "#000000"  # 黑色（经典）
bar_color = "#3498DB"  # 蓝色（现代）
bar_color = "#E74C3C"  # 红色（活力）
bar_color = "#2ECC71"  # 绿色（清新）
bar_color = "#9B59B6"  # 紫色（优雅）
```

### 📐 对齐配置 `[alignment]`

| 参数 | 可选值 | 效果 |
|------|--------|------|
| `vertical_align` | `"center"` | 频谱条垂直居中 |
|  | `"top"` | 频谱条顶部对齐 |
|  | `"bottom"` | 频谱条底部对齐 |

## 📝 使用示例

### 示例 1: 生成黑色居中频谱图

```toml
[svg]
bar_color = "#000000"
border_radius = 0

[alignment]
vertical_align = "center"
```

### 示例 2: 生成彩色圆角底部对齐频谱图

```toml
[svg]
bar_color = "#FF6B6B"
border_radius = 3

[alignment]
vertical_align = "bottom"
```

### 示例 3: 为长音频生成紧凑频谱图

```toml
[spectrum]
bars_per_second = 5  # 减少频谱条密度

[svg]
bar_width = 4        # 更窄的频谱条
bar_spacing = 5      # 更小的间距
height = 100         # 降低高度
```

## 📂 项目结构

```
.
├── audio_spectrum_svg.py    # 主程序脚本
├── config.toml              # 默认配置文件
├── example_config.toml      # 示例配置文件
├── README.md                # 本文档
└── requirements.txt         # 依赖列表（可选）
```

## 🔧 高级用法

### 作为 Python 模块使用

```python
from audio_spectrum_svg import AudioSpectrumSVG

# 创建生成器实例
generator = AudioSpectrumSVG('config.toml')

# 处理音频
generator.process('input.mp3', 'output.svg')

# 或分步处理
generator.load_audio('input.mp3')
spectrum = generator.calculate_spectrum()
generator.generate_svg(spectrum, 'output.svg')
```

### 批量处理多个音频文件

```python
import os
from audio_spectrum_svg import AudioSpectrumSVG

generator = AudioSpectrumSVG('config.toml')

audio_files = ['audio1.mp3', 'audio2.wav', 'audio3.flac']
for audio_file in audio_files:
    output_file = os.path.splitext(audio_file)[0] + '.svg'
    generator.process(audio_file, output_file)
    print(f'已处理: {audio_file} -> {output_file}')
```

## 🐛 常见问题

### Q: 提示找不到 ffmpeg？
A: MP3 等格式需要 ffmpeg 支持，请安装 ffmpeg 并确保在系统 PATH 中。

### Q: 生成的频谱图太密集或太稀疏？
A: 调整 `bars_per_second` 参数。增大数值会生成更多频谱条，减小则更稀疏。

### Q: 频谱条高度不明显？
A: 尝试调整以下参数：
- 增大 `max_bar_height_percent`
- 减小 `min_bar_height`
- 调整 `time_window` 大小

### Q: SVG 文件太大？
A: 对于长音频，减小 `bars_per_second` 值以减少频谱条数量。

## 📄 许可证

本项目使用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

**享受创作音频可视化作品的乐趣！** 🎉
