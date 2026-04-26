# 🚀 NewApi 多平台自动签到

本项目用于实现基于 New API / One API 架构的 AI 中转站自动签到。支持通过 GitHub Actions 实现每日定时自动运行。

## 🛠️ 环境准备

1. **Python 版本**: 3.10+
2. **核心依赖**: `curl_cffi` (用于模拟浏览器指纹，绕过基础反爬)
3. **部署方式**: 本地运行 或 GitHub Actions 自动化

---

## 🔑 关键变量获取指南

为了保护账号安全，脚本统一通过环境变量读取敏感信息。以下是获取这些变量的方法：

### 1. 盒子镜像 (Boxying)
- **站点地址**: `https://www.boxying.com`
- **获取 BOXYING_SESSION**:
    1. 使用 Chrome 浏览器登录站点。
    2. 按下 `F12` 打开开发者工具，切换到 **Network (网络)** 标签。
    3. 刷新页面或点击任意操作，在左侧找到一个请求，查看 **Cookies**。
    4. 找到名为 `session` 的值（通常以 `MTc3...` 开头），这就是你的 Session。
- **获取 BOXYING_API_USER**:
    1. 在控制台或用户信息页，找到你的用户 ID（例如 `754`）。
    2. 也可以在 Network 请求的 **Headers** 中找到 `new-api-user` 字段。

---

## ⚙️ 配置 GitHub Actions

1. Fork 或上传代码到你的仓库。
2. 进入仓库的 **Settings -> Secrets and variables -> Actions**。
3. 点击 **New repository secret**，依次添加以下变量：

| 变量名 | 描述 | 示例 |
| :--- | :--- | :--- |
| `BOXYING_SESSION` | Boxying 登录会话 Cookie | `MTc3...` |
| `BOXYING_API_USER` | Boxying 用户 ID | `754` |

---

## 📂 项目结构与分类

目前已支持以下平台，后续将持续更新：

### 🟢 签到类 (Check-in)
* **Boxying (盒子镜像)**: 
    * 脚本路径: `asia/creat/boxying-checkin.py`
    * 特点: 基于 `reward_center` 接口，模拟浏览器 Alpha 版逻辑。

### 🟡 待适配平台 (Upcoming)
* [ ] 更多基于 One API 的站点...
* [ ] 更多基于 V2Board 的站点...

---

## ⏰ 定时任务说明

工作流默认配置在 **北京时间每天上午 09:10** 运行。
你可以通过修改 `.github/workflows/checkin.yml` 中的 `cron` 表达式来调整时间。