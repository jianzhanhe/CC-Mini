# CC-Mini

简化版 Codex 配置切换工具。填写 API 地址、密钥和模型后，一键写入 Codex 配置文件，方便使用第三方中转 API。

## 功能介绍

- **接口地址**：默认 `http://api.h5.namawang.com/v1`，可自定义
- **API 密钥**：密码框输入，不会明文显示；右侧「获取」按钮可打开控制台页面
- **模型名称**：支持手动输入，并提供常用模型快捷选择
- **立即切换**：用 `config.txt` 模板覆盖 `~/.codex/config.toml`，并将 API Key 写入 `~/.codex/auth.json`
- **文档按钮**：标题栏「📖 文档」可打开 [http://docs.h5.namawang.com/](http://docs.h5.namawang.com/)

## 项目结构

```
.
├── codex_config.py   # 主程序（GUI + 配置写入逻辑）
├── config.txt        # config.toml 模板，打包时会内嵌进 exe
├── requirements.txt  # 依赖说明
├── CC-Mini.spec      # PyInstaller 打包配置（首次打包后自动生成）
├── README.md         # 项目说明
├── build/            # 打包中间文件（可删除）
└── dist/
    └── CC-Mini.exe   # 打包后的可执行文件
```

## 修改的配置文件

| 文件 | 路径 | 作用 |
|------|------|------|
| `config.toml` | `~/.codex/config.toml` | Codex 主配置（接口地址、模型等） |
| `auth.json` | `~/.codex/auth.json` | 保存 `OPENAI_API_KEY` |

切换时会替换模板中的以下字段：

- `base_url`
- `model`
- `review_model`

其余配置项保持 `config.txt` 模板中的默认值。

## 使用的模块 / 扩展

### 运行时（Python 标准库，无需 pip 安装）

| 模块 | 作用 |
|------|------|
| `tkinter` | 桌面 GUI 界面 |
| `json` | 读写 `auth.json` |
| `re` | 替换 `config.txt` 模板中的配置项 |
| `os` | 路径处理、创建 `.codex` 目录 |
| `sys` | 判断是否为 PyInstaller 打包环境，定位内嵌的 `config.txt` |
| `webbrowser` | 打开 API 控制台、使用文档等网页链接 |

> 本程序**不依赖第三方 Python 包**，只要系统自带 Python 且包含 tkinter 即可运行。

### 打包时（仅开发者需要）

| 工具 | 作用 |
|------|------|
| **PyInstaller** | 将 Python 程序打包成独立 `.exe`，方便在没有 Python 的电脑上运行 |

## 环境要求

- **直接运行源码**：Python 3.8+
- **运行 exe**：Windows 10/11，无需安装 Python
- **打包**：Python 3.8+、PyInstaller

## 使用方法

### 方式一：直接运行 Python 源码

```bash
python codex_config.py
```

### 方式二：运行打包好的 exe

双击 `dist/CC-Mini.exe` 即可。

1. 填写或确认 **接口地址**
2. 填写 **API 密钥**（可点「获取」去官网创建）
3. 选择或输入 **模型名称**
4. 点击 **⚡ 立即切换**
5. 重启 Codex 使配置生效

## 如何打包成 exe

在项目目录下执行：

```bash
python -m PyInstaller --onefile --noconsole --name "CC-Mini" --add-data "config.txt;." codex_config.py
```

参数说明：

| 参数 | 说明 |
|------|------|
| `--onefile` | 打包成单个 exe 文件 |
| `--noconsole` | 不显示黑色命令行窗口 |
| `--name "CC-Mini"` | 输出文件名 |
| `--add-data "config.txt;."` | 将模板文件内嵌进 exe（Windows 用 `;` 分隔） |

打包完成后，可执行文件位于：

```
dist/CC-Mini.exe
```

也可以直接使用已生成的 spec 文件重新打包：

```bash
python -m PyInstaller CC-Mini.spec
```

### 打包注意事项

- 首次运行 exe 可能稍慢，属于 PyInstaller 解压资源的正常现象
- 部分杀毒软件可能对 PyInstaller 打包程序误报，可选择「仍要运行」
- 修改 `config.txt` 后需要重新打包，exe 才会使用新模板
- `build/` 目录为中间产物，可删除；`dist/CC-Mini.exe` 才是最终产物

## 相关链接

- API 控制台：http://api.h5.namawang.com/
- 使用文档：http://docs.h5.namawang.com/

## 许可

本项目仅供个人学习与交流使用。
