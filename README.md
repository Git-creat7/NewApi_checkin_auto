# NewApi 多平台自动签到

本项目用于 New API / One API 架构站点的自动签到，适合部署在 GitHub Actions 中按天定时运行。

## 支持的平台

| 平台 | 脚本路径 | 认证方式 | 主要环境变量 |
|:-----|:--------|:--------|:------------|
| [Boxying](https://www.boxying.com/register?aff=henf) | `checkin/boxying/checkin.py` | Session Cookie | `BOXYING_SESSION` `BOXYING_API_USER` |
| [Elysiver](https://elysiver.h-e.top/register?aff=vGW7) | `checkin/elysiver/checkin.py` | 令牌 | `ELYSIVER_ACCESS_TOKEN` `ELYSIVER_API_USER` |
| [N1Neman](https://mynewapi.n1neman.fun/) | `checkin/n1neman/checkin.py` | 令牌 | `N1NEMAN_ACCESS_TOKEN` `N1NEMAN_API_USER` |
| [Jiuuij](https://jiuuij.de5.net/) | `checkin/jiuuij/checkin.py` | 令牌 | `JIUUIJ_ACCESS_TOKEN` `JIUUIJ_API_USER` |
| [AnyRouter](https://anyrouter.top/) | `checkin/anyrouter/checkin.py` | Session Cookie | `ANYROUTER_COOKIE` `ANYROUTER_API_USER` |
| [君の公益](https://muyuan.do/) | `checkin/muyuan/checkin.py` | 令牌 | `MUYUAN_ACCESS_TOKEN` `MUYUAN_API_USER` |
| [Sub2](https://sub.100xlabs.space/) | `checkin/sub2/checkin.py` | 令牌 | `SUB2_ACCESS_TOKEN` `SUB2_API_USER` |

## 运行环境

- Python `3.10+`
- 依赖见 `requirements.txt`

```bash
pip install -r requirements.txt
```

## 认证方式说明

### 令牌认证（推荐）

在网站 **个人设置 → 账户管理 → 安全设置** 中点击 **生成令牌**，复制后填入对应的 `*_ACCESS_TOKEN`。令牌不会自动过期，比 Session Cookie 更稳定。

需要同时提供 `*_API_USER`（用户 ID），可从浏览器 F12 → Application → Local Storage → `user` → `id` 获取。

### Session Cookie 认证

部分站点不支持令牌认证时使用。从浏览器 F12 → Application → Cookies 中复制 `session` 值。Session 可能过期，失效后需重新获取。

## 环境变量说明

### 通用（可选）

- `PUSHPLUS_TOKEN` — PushPlus 推送 Token（仅 Boxying 脚本支持）

### Boxying

- `BOXYING_SESSION` — 浏览器 Cookie 中的 `session`
- `BOXYING_API_USER` — 用户 ID
- `BOXYING_TIMEOUT` — 请求超时秒数，默认 `30`

### Elysiver

- `ELYSIVER_ACCESS_TOKEN` — 系统访问令牌
- `ELYSIVER_API_USER` — 用户 ID
- `ELYSIVER_TIMEOUT` — 请求超时秒数，默认 `30`

### N1Neman

- `N1NEMAN_ACCESS_TOKEN` — 系统访问令牌
- `N1NEMAN_API_USER` — 用户 ID
- `N1NEMAN_TIMEOUT` — 请求超时秒数，默认 `30`

### Jiuuij

- `JIUUIJ_ACCESS_TOKEN` — 系统访问令牌
- `JIUUIJ_API_USER` — 用户 ID
- `JIUUIJ_TIMEOUT` — 请求超时秒数，默认 `30`

### AnyRouter

- `ANYROUTER_COOKIE` — 浏览器 Cookie 字符串（多个 cookie 用 `; ` 连接）
- `ANYROUTER_API_USER` — 用户 ID
- `ANYROUTER_TIMEOUT` — 请求超时秒数，默认 `30`

### 君の公益

- `MUYUAN_ACCESS_TOKEN` — 系统访问令牌
- `MUYUAN_API_USER` — 用户 ID
- `MUYUAN_TIMEOUT` — 请求超时秒数，默认 `30`

### Sub2

- `SUB2_ACCESS_TOKEN` — 系统访问令牌
- `SUB2_API_USER` — 用户 ID
- `SUB2_TIMEOUT` — 请求超时秒数，默认 `30`

## GitHub Actions 配置

### 方式一：使用脚本批量设置（推荐）

```bash
# 安装并登录 gh CLI
gh auth login

# 运行配置脚本
bash setup-secrets.sh
```

### 方式二：手动设置

进入仓库的 `Settings → Secrets and variables → Actions`，按需添加：

| Secret 名称 | 用途 |
|:------------|:-----|
| `BOXYING_SESSION` | Boxying 登录 Session |
| `BOXYING_API_USER` | Boxying 用户 ID |
| `ELYSIVER_ACCESS_TOKEN` | Elysiver 系统访问令牌 |
| `ELYSIVER_API_USER` | Elysiver 用户 ID |
| `N1NEMAN_ACCESS_TOKEN` | N1Neman 系统访问令牌 |
| `N1NEMAN_API_USER` | N1Neman 用户 ID |
| `JIUUIJ_ACCESS_TOKEN` | Jiuuij 系统访问令牌 |
| `JIUUIJ_API_USER` | Jiuuij 用户 ID |
| `ANYROUTER_COOKIE` | AnyRouter Cookie 字符串 |
| `ANYROUTER_API_USER` | AnyRouter 用户 ID |
| `MUYUAN_ACCESS_TOKEN` | 君の公益 系统访问令牌 |
| `MUYUAN_API_USER` | 君の公益 用户 ID |
| `SUB2_ACCESS_TOKEN` | Sub2 系统访问令牌 |
| `SUB2_API_USER` | Sub2 用户 ID |
| `PUSHPLUS_TOKEN` | PushPlus 推送 Token（可选） |

### 方式三：命令行设置

```bash
gh secret set BOXYING_SESSION -b "你的Session"
gh secret set BOXYING_API_USER -b "你的用户ID"
```

## 工作流

当前仓库包含七个工作流文件：

- `.github/workflows/boxying.yml`
- `.github/workflows/elysiver.yml`
- `.github/workflows/n1neman.yml`
- `.github/workflows/jiuuij.yml`
- `.github/workflows/anyrouter.yml`
- `.github/workflows/muyuan.yml`
- `.github/workflows/sub2.yml`

每个工作流在北京时间 9:00-12:00 之间触发，并随机延迟 0-180 分钟后执行签到，避免扎堆。也支持手动触发 `workflow_dispatch`。

## 本地运行

PowerShell 示例：

```powershell
$env:BOXYING_SESSION="你的Session"; $env:BOXYING_API_USER="你的ID"; python checkin/boxying/checkin.py
$env:ELYSIVER_ACCESS_TOKEN="你的令牌"; $env:ELYSIVER_API_USER="你的ID"; python checkin/elysiver/checkin.py
$env:N1NEMAN_ACCESS_TOKEN="你的令牌"; $env:N1NEMAN_API_USER="你的ID"; python checkin/n1neman/checkin.py
$env:JIUUIJ_ACCESS_TOKEN="你的令牌"; $env:JIUUIJ_API_USER="你的ID"; python checkin/jiuuij/checkin.py
$env:ANYROUTER_COOKIE="你的Cookie"; $env:ANYROUTER_API_USER="你的ID"; python checkin/anyrouter/checkin.py
$env:MUYUAN_ACCESS_TOKEN="你的令牌"; $env:MUYUAN_API_USER="你的ID"; python checkin/muyuan/checkin.py
$env:SUB2_ACCESS_TOKEN="你的令牌"; $env:SUB2_API_USER="你的ID"; python checkin/sub2/checkin.py
```

Git Bash 示例：

```bash
BOXYING_SESSION="你的Session" BOXYING_API_USER="你的ID" python checkin/boxying/checkin.py
```

## 免责声明

1. 本项目仅供学习与研究自动化流程使用。
2. 自动签到可能违反目标站点服务条款，请自行评估风险。
3. 因使用本项目导致的账号、额度或其他损失，由使用者自行承担。
