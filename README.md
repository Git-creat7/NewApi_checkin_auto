# NewApi 多平台自动签到

本项目用于 New API / One API 架构站点的自动签到，适合部署在 GitHub Actions 中按天定时运行。

当前仓库已内置两个签到脚本，并支持使用 `PUSHPLUS_TOKEN` 发送 PushPlus 通知。

## 支持的平台

| 平台          | 脚本路径 | 主要环境变量 |
|:------------| :--- | :--- |
| [Boxying](https://www.boxying.com/register?aff=henf) | `checkin/boxying/checkin.py` | `BOXYING_SESSION` `BOXYING_API_USER` |
| [XEM](http://new.xem8k5.top:3000/register?aff=Byib)     | `checkin/xem/checkin.py` | `XEM_SESSION` `XEM_API_USER` |

## 运行环境

- Python `3.10+`
- 依赖见 `requirements.txt`

本地安装依赖：

```bash
pip install -r requirements.txt
```

## 环境变量说明

### Boxying


- `BOXYING_SESSION`
  登录后浏览器 Cookie 中的 `session`
- `BOXYING_API_USER`
  当前账号的用户 ID
- `BOXYING_TIMEOUT`
  请求超时秒数，默认 `30`

### XEM


- `XEM_SESSION`
  登录后浏览器 Cookie 中的 `session`
- `XEM_API_USER`
  当前账号的用户 ID
- `XEM_TIMEOUT`
  请求超时秒数，默认 `30`

### PushPlus 通知

- `PUSHPLUS_TOKEN`
  可选。配置后，签到成功或失败都会推送通知。

## 如何获取 Session 和用户 ID

1. 用浏览器登录目标站点。
2. 按 `F12` 打开开发者工具。
3. 在 `Network` 面板中刷新页面，选择任意一个已登录请求。
4. 在请求的 Cookie 中找到 `session`，填入对应的 `*_SESSION`。
5. 在请求头或用户信息接口返回中找到当前账号 ID，填入对应的 `*_API_USER`。

## GitHub Actions 配置

进入仓库的 `Settings -> Secrets and variables -> Actions`，按需添加以下 Secrets：

| Secret 名称 | 用途 |
| :--- | :--- |
| `BOXYING_SESSION` | Boxying 登录 Session |
| `BOXYING_API_USER` | Boxying 用户 ID |
| `XEM_SESSION` | XEM 登录 Session |
| `XEM_API_USER` | XEM 用户 ID |
| `PUSHPLUS_TOKEN` | PushPlus 推送 Token，可选 |

## 工作流

当前仓库包含两个工作流文件：

- `.github/workflows/boxying.yml`
- `.github/workflows/xem.yml`

默认使用 GitHub Actions 每天定时执行一次，也支持手动触发 `workflow_dispatch`。

如果你想调整执行时间，可以修改对应 workflow 中的 `cron` 表达式。

## 本地运行

示例：

```bash
python checkin/boxying/checkin.py
python checkin/xem/checkin.py
```

运行前请先设置好对应环境变量。

## PushPlus 推送效果

配置 `PUSHPLUS_TOKEN` 后，脚本会在以下场景发送通知：

- 签到成功
- 使用 session 回退后签到成功
- 签到失败

## 免责声明

1. 本项目仅供学习与研究自动化流程使用。
2. 自动签到可能违反目标站点服务条款，请自行评估风险。
3. 因使用本项目导致的账号、额度或其他损失，由使用者自行承担。
