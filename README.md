# NewApi 多平台自动签到

本项目用于 New API / One API 架构站点的自动签到，适合部署在 GitHub Actions 中按天定时运行。

## 支持的平台

| 平台 | 脚本路径 | 认证方式 | 主要环境变量 |
|:-----|:--------|:--------|:------------|
| [Boxying](https://www.boxying.com/register?aff=henf) | `checkin/boxying/checkin.py` | 令牌 / Session Cookie | `BOXYING_ACCESS_TOKEN` `BOXYING_SESSION` `BOXYING_API_USER` |
| [Elysiver](https://elysiver.h-e.top/register?aff=vGW7) | `checkin/elysiver/checkin.py` | 令牌 | `ELYSIVER_ACCESS_TOKEN` `ELYSIVER_API_USER` |
| [N1Neman](https://mynewapi.n1neman.fun/) | `checkin/n1neman/checkin.py` | 令牌 | `N1NEMAN_ACCESS_TOKEN` `N1NEMAN_API_USER` |
| [Jiuuij](https://jiuuij.de5.net/) | `checkin/jiuuij/checkin.py` | 令牌 | `JIUUIJ_ACCESS_TOKEN` `JIUUIJ_API_USER` |
| [91](https://api.7r.fit/) | `checkin/7rfit/checkin.py` | 令牌 | `R91_ACCESS_TOKEN` `R91_API_USER` |
| [CHY公益站](https://chybenzun.top/) | `checkin/chy/checkin.py` | 令牌 | `CHY_ACCESS_TOKEN` `CHY_API_USER` |
| [CHY订阅](https://dy.chybenzun.top/) | `checkin/chysub/checkin.py` | Cookie | `CHYSUB_COOKIE` 或 `CHYSUB_SESSION`+`CHYSUB_CF_CLEARANCE` |
| [Mofas](https://www.mofas.one/) | `checkin/mofas/checkin.py` | 令牌 | `MOFAS_ACCESS_TOKEN` `MOFAS_API_USER` |

| [Lan](https://ai.venlacy.com/) | `checkin/venlacy/checkin.py` | 令牌 | `VENLACY_ACCESS_TOKEN` `VENLACY_API_USER` |
| [CUN](https://www.cun.ai/) | `checkin/cun/checkin.py` | 令牌 | `CUN_ACCESS_TOKEN` `CUN_API_USER` |

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

令牌站点共用 `checkin/token_site.py` 中的通用签到实现，各站点脚本只保留平台名称、环境变量前缀、默认地址和货币配置。

### Session Cookie 认证

部分站点不支持令牌认证时使用。从浏览器 F12 → Application → Cookies 中复制 `session` 值。Session 可能过期，失效后需重新获取。

## 环境变量说明

### 通用（可选）

- `PUSHPLUS_TOKEN` — 统一工作流 PushPlus 推送 Token

### Boxying

- `BOXYING_ACCESS_TOKEN` — 系统访问令牌（优先使用）
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

### 91

- `R91_ACCESS_TOKEN` — 系统访问令牌
- `R91_API_USER` — 用户 ID
- `R91_TIMEOUT` — 请求超时秒数，默认 `30`

### CHY公益站

- `CHY_ACCESS_TOKEN` — 系统访问令牌
- `CHY_API_USER` — 用户 ID
- `CHY_TIMEOUT` — 请求超时秒数，默认 `30`

### CHY订阅

- `CHYSUB_COOKIE` — 浏览器完整 Cookie（推荐，含 `cf_clearance`、`chy_session` 等）
- `CHYSUB_SESSION` — 仅 `chy_session` 值（可与 CF 字段拆开配置）
- `CHYSUB_CF_CLEARANCE` — Cloudflare `cf_clearance`（可选）
- `CHYSUB_TIMEOUT` — 请求超时秒数，默认 `30`

Cookie 会过期（尤其 `cf_clearance`），失效后需重新从浏览器复制。

### Mofas


- `MOFAS_ACCESS_TOKEN` — 系统访问令牌
- `MOFAS_API_USER` — 用户 ID
- `MOFAS_TIMEOUT` — 请求超时秒数，默认 `30`

### Lan (Venlacy)

- `VENLACY_ACCESS_TOKEN` — 系统访问令牌
- `VENLACY_API_USER` — 用户 ID
- `VENLACY_TIMEOUT` — 请求超时秒数，默认 `30`

### CUN

- `CUN_ACCESS_TOKEN` — 系统访问令牌
- `CUN_API_USER` — 用户 ID
- `CUN_TIMEOUT` — 请求超时秒数，默认 `30`

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
| `BOXYING_ACCESS_TOKEN` | Boxying 系统访问令牌 |
| `BOXYING_SESSION` | Boxying 登录 Session（令牌不可用时兜底） |
| `BOXYING_API_USER` | Boxying 用户 ID |
| `ELYSIVER_ACCESS_TOKEN` | Elysiver 系统访问令牌 |
| `ELYSIVER_API_USER` | Elysiver 用户 ID |
| `N1NEMAN_ACCESS_TOKEN` | N1Neman 系统访问令牌 |
| `N1NEMAN_API_USER` | N1Neman 用户 ID |
| `JIUUIJ_ACCESS_TOKEN` | Jiuuij 系统访问令牌 |
| `JIUUIJ_API_USER` | Jiuuij 用户 ID |
| `R91_ACCESS_TOKEN` | 91 系统访问令牌 |
| `R91_API_USER` | 91 用户 ID |
| `CHY_ACCESS_TOKEN` | CHY公益站 系统访问令牌 |
| `CHY_API_USER` | CHY公益站 用户 ID |
| `CHYSUB_COOKIE` | CHY订阅 完整 Cookie |
| `CHYSUB_SESSION` | CHY订阅 chy_session（可选） |
| `CHYSUB_CF_CLEARANCE` | CHY订阅 cf_clearance（可选） |
| `MOFAS_ACCESS_TOKEN` | Mofas 系统访问令牌 |

| `MOFAS_API_USER` | Mofas 用户 ID |
| `VENLACY_ACCESS_TOKEN` | Lan 系统访问令牌 |
| `VENLACY_API_USER` | Lan 用户 ID |
| `CUN_ACCESS_TOKEN` | CUN 系统访问令牌 |
| `CUN_API_USER` | CUN 用户 ID |
| `PUSHPLUS_TOKEN` | PushPlus 推送 Token（可选） |

### 方式三：命令行设置

```bash
gh secret set BOXYING_SESSION -b "你的Session"
gh secret set BOXYING_API_USER -b "你的用户ID"
```

## 工作流

只有一个统一工作流，每天运行一次：

- `.github/workflows/checkin-all.yml` — 统一签到 + 汇总推送
- `.github/workflows/validate-credentials.yml` — 手动校验凭据，只读取用户信息，不执行签到

触发时间：UTC 3:00（北京时间 11:00），再随机延迟 10-110 分钟，实际执行时间在北京时间 **11:10-12:50** 之间随机。

也支持手动触发 `workflow_dispatch`。更换令牌后建议先运行 `validate-credentials` 确认 ID 和令牌匹配。

## PushPlus 推送

统一工作流会在所有平台签到完成后，通过 PushPlus 发送一条汇总消息，包含各平台的签到状态、今日奖励和当前余额。

需配置 Secret `PUSHPLUS_TOKEN`。未配置则跳过推送。

## 本地运行

PowerShell 示例：

```powershell
$env:BOXYING_ACCESS_TOKEN="你的令牌"; $env:BOXYING_API_USER="你的ID"; python checkin/boxying/checkin.py
$env:ELYSIVER_ACCESS_TOKEN="你的令牌"; $env:ELYSIVER_API_USER="你的ID"; python checkin/elysiver/checkin.py
$env:N1NEMAN_ACCESS_TOKEN="你的令牌"; $env:N1NEMAN_API_USER="你的ID"; python checkin/n1neman/checkin.py
$env:JIUUIJ_ACCESS_TOKEN="你的令牌"; $env:JIUUIJ_API_USER="你的ID"; python checkin/jiuuij/checkin.py
$env:R91_ACCESS_TOKEN="你的令牌"; $env:R91_API_USER="你的ID"; python checkin/7rfit/checkin.py
$env:CHY_ACCESS_TOKEN="你的令牌"; $env:CHY_API_USER="你的ID"; python checkin/chy/checkin.py
$env:CHYSUB_COOKIE="cf_clearance=...; chy_session=..."; python checkin/chysub/checkin.py
$env:MOFAS_ACCESS_TOKEN="你的令牌"; $env:MOFAS_API_USER="你的ID"; python checkin/mofas/checkin.py

$env:VENLACY_ACCESS_TOKEN="你的令牌"; $env:VENLACY_API_USER="你的ID"; python checkin/venlacy/checkin.py
$env:CUN_ACCESS_TOKEN="你的令牌"; $env:CUN_API_USER="你的ID"; python checkin/cun/checkin.py
```

统一签到 + 推送：

```powershell
$env:PUSHPLUS_TOKEN="你的Token"; python checkin_all.py
```

Git Bash 示例：

```bash
BOXYING_SESSION="你的Session" BOXYING_API_USER="你的ID" python checkin/boxying/checkin.py
```

## 免责声明

1. 本项目仅供学习与研究自动化流程使用。
2. 自动签到可能违反目标站点服务条款，请自行评估风险。
3. 因使用本项目导致的账号、额度或其他损失，由使用者自行承担。
