# 🛡️ ScreenCloak (屏幕防窥哨兵)

<div align="center">

**专为开发者与远程会议设计的轻量级屏幕共享代码防窥与打码滤镜。**  
*A lightweight, click-through screen privacy filter & censor bar for live screen sharing and recording.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-lightgrey.svg)](https://microsoft.com)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0%20External-success.svg)](https://github.com/Mianm-l/screen-cloak)
[![Meeting Compatible](https://img.shields.io/badge/Compatible-Tencent%20Meeting%20%7C%20Zoom%20%7C%20Feishu-orange.svg)](https://github.com/Mianm-l/screen-cloak)

[核心痛点](#-为什么需要-screencloak) • [工作原理](#-核心黑科技鼠标穿透与合成采集) • [功能特性](#-功能特性) • [快捷键说明](#-全局快捷键) • [快速开始](#-快速开始)

</div>

---

## 💡 为什么需要 ScreenCloak？

在远程技术评审、Bug 排查开会、或者录制教学视频时，开发者常常处于两难境地：
* **投屏不敢切编辑器**：生怕切到 `application.yml` 露出数据库密码，或者在终端敲命令行时不小心回显了内网 IP、SSH 密钥或带 Token 的接口出参；
* **事后录像极度危险**：会议录播会自动同步到企业云盘或发给外包伙伴，一旦密钥被录进去就是严重的信息安全事故；
* **传统工具不管用**：市面上的隐私扩展只能管 Chrome 浏览器网页，一旦切到 VS Code、IDEA、Postman 或 Terminal，立刻全面裸奔！

**ScreenCloak 是一个常驻桌面的轻量遮罩工具：在你的屏幕敏感区域覆盖帅气的绝密打码条，开会录屏死死遮住，但你的鼠标可以彻底穿透遮罩继续写代码！**

---

## 🔬 核心黑科技：鼠标穿透与合成采集

```
┌──────────────────────────────────────────────────────────┐
│ 📺 物理屏幕呈现                                            │
│                                                          │
│   VS Code 编辑器 / 终端 / Postman                         │
│   ┌──────────────────────────────────────────────────┐   │
│   │ db.password: 🔒 [ SENSITIVE DATA REDACTED ]     │   │
│   └──────────────────────────────────────────────────┘   │
│            ▲                                             │
│            │  (鼠标点击、拖选、滚轮 100% 穿透执行！)         │
│            │                                             │
│   你依然可以正常在遮罩下方点击光标、输入修改代码！          │
└──────────────────────────────────────────────────────────┘
                            │
                            ▼ Windows DWM 桌面合成采集
┌──────────────────────────────────────────────────────────┐
│ 👥 腾讯会议 / Zoom / 飞书 参会人员看到的画面               │
│                                                          │
│   敏感区域被赛博绝密条死死焊住，完全看不到底层真实密码与密钥！ │
└──────────────────────────────────────────────────────────┘
```

1. **Windows 原生点击穿透 (`WS_EX_TRANSPARENT`)**：
   通过调用 Windows 原生分层击穿 API，防窥遮罩保持视觉最顶层（Topmost），但将所有鼠标与指针消息无损穿透派发给底层的 IDE。
2. **腾讯会议/Zoom 天然兼容**：
   现代会议软件在共享“桌面/屏幕”时，会通过桌面合成器（DWM）抓取最终合成画面。遮罩层会被完整采集推流，达成 100% 物理级遮挡。

---

## ✨ 功能特性

- ⚡ **零外部第三方依赖**：纯 Python 标准库 + Windows 原生 API 实现，不需要 `pip install` 任何重量级 C++ 运行时或大包，开箱即用。
- 🎯 **快速暗屏划框（Snipping-Tool 风格）**：点击「🎯 划框」或快捷键，屏幕微暗，随手一拉即可精准覆盖任意长方形敏感区域。
- 🖱️ **一键穿透锁定**：
  - **编辑模式 (Edit Mode)**：显示拖拽句柄与调整手柄，自由移动、拉伸大小、关闭；
  - **锁定穿透模式 (Locked Mode)**：句柄与边框隐形，化身绝密黑条，**鼠标完全穿透至下层编辑器，开会写代码两不耽误！**
- 🎨 **多套赛博打码风格**：
  - **绝密黑金条 (Redacted Obsidian)**：暗黑底色配经典黑金标志 `[ 🔒 SENSITIVE DATA REDACTED ]`；
  - **高危警示条纹 (Warning Classified)**：黄黑警示工业条纹 `[ ⚠️ CLASSIFIED - PROTECTED ]`；
  - **纯黑哑光 (Pure Black)**：极简纯黑方块，彻底遮盖。
- 📋 **布局预设一键存取 (Presets)**：
  - 支持将当前排布好的防窥条（如“VS Code 终端区 + Postman 头部”）保存为预设，下次开会一键载入恢复！
- 👁️ **全局一键隐身/显现**：非敏感场景下一键隐藏所有遮罩，需要时秒级恢复。

---

## ⌨️ 全局快捷键

哪怕你正在全屏写代码，无需切回控制器，随时随地可用键盘触发：

| 快捷键 | 功能说明 |
| :--- | :--- |
| **`Ctrl + Alt + C`** | **切换锁定穿透 / 编辑模式**（开会时一键锁死并开启鼠标穿透） |
| **`Ctrl + Alt + V`** | **瞬时偷瞄（Peek）**（瞬间淡化为 20% 透明看清底下代码，再按瞬间恢复绝密遮盖！） |
| **`Ctrl + Alt + N`** | **快速新建** 一个居中防窥条 |
| **`Ctrl + Alt + H`** | **全局隐藏 / 恢复** 所有防窥条 |

---

## 👁️ 自己想看底下代码怎么办？（双重透视方案）

ScreenCloak 专为解决主讲人“看不清自己写的代码”设计了两种优雅解法：

1. **瞬时偷瞄（Quick Peek）**：
   * 键盘直接按 **`Ctrl + Alt + V`**（或点击 Dock 上的 `👁️ 偷瞄`）；
   * 防窥条立刻淡化为 **20% 半透明**，底下的代码、变量名、行号纤毫毕现；
   * 看完后随手再按一次 `Ctrl + Alt + V`，瞬间恢复 100% 纯黑封死！
2. **单向微透档位（85% / 70% 模式）**：
   * 点击 Dock 上的 `🌓 100%` 可切换为 `🌓 85%` 或 `🌓 70%`；
   * **在你的高分屏物理屏幕面前**：肉眼贴近屏幕，能清晰看到底下的代码轮廓与行号；
   * **但在腾讯会议/Zoom 视频推流端**：经过 H.264 视频有损压缩和丢帧码率压缩后，85% 的暗底会直接把微弱的字符彻底压成一团糊掉的黑斑，外人完全无法分辨！

---

## 🚀 快速开始 (Windows)

### 方式一：双击直接运行 (免黑框)

克隆项目后，直接双击 `start.bat` 即可静默唤起顶部悬浮控制胶囊！

### 方式二：命令行运行

```bash
git clone https://github.com/Mianm-l/screen-cloak.git
cd screen-cloak

python main.py
```

---

## 📄 开源许可证

本项目基于 [MIT 许可证](LICENSE) 开源。欢迎大家试用并提交 PR 与建议！
