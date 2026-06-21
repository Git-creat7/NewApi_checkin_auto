#!/usr/bin/env python3
import os
import sys
import importlib
from datetime import datetime, timezone

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from curl_cffi import requests


PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "").strip()


PLATFORMS = [
    ("boxying", "checkin.boxying.checkin"),
    ("elysiver", "checkin.elysiver.checkin"),
    ("n1neman", "checkin.n1neman.checkin"),
    ("jiuuij", "checkin.jiuuij.checkin"),
    ("muyuan", "checkin.muyuan.checkin"),
    ("7rfit", "checkin.7rfit.checkin"),
    ("maoyulin", "checkin.maoyulin.checkin"),
    ("anyrouter", "checkin.anyrouter.checkin"),
]


def quota_to_currency(quota, currency: str = "$") -> str:
    if quota is None:
        return "-"
    try:
        amount = int(quota) / 500000
    except (TypeError, ValueError):
        return str(quota)
    if currency == "$":
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"


def run_platform(name: str, module_path: str) -> dict:
    env_prefix = name.upper().replace("-", "_")
    has_creds = bool(os.getenv(f"{env_prefix}_ACCESS_TOKEN", "") or os.getenv(f"{env_prefix}_SESSION", "") or os.getenv(f"{env_prefix}_COOKIE", ""))
    if not has_creds:
        print(f"\n⏭️ {name}: 未配置凭据，跳过")
        return {"platform": name, "success": True, "message": "未配置凭据，跳过", "reward": None, "balance": None, "skipped": True}

    print(f"\n{'='*40}")
    print(f"▶ 开始签到: {name}")
    print(f"{'='*40}")
    try:
        mod = importlib.import_module(module_path)
        return mod.main()
    except Exception as exc:
        print(f"❌ {name} 签到异常: {exc}")
        return {"platform": name, "success": False, "message": str(exc), "reward": None, "balance": None}


def build_html(results: list) -> str:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    rows = ""
    for r in results:
        if r.get("skipped"):
            continue
        platform = r.get("platform", "?")
        status = "✅" if r.get("success") else "❌"
        currency = r.get("currency") or "$"
        reward = quota_to_currency(r.get("reward"), currency)
        balance = quota_to_currency(r.get("balance"), currency)
        msg = r.get("message", "")
        rows += f"<tr><td>{platform}</td><td>{status}</td><td>{reward}</td><td>{balance}</td><td>{msg}</td></tr>"

    total_rewards = {}
    for r in results:
        if r.get("reward") is not None:
            try:
                currency = r.get("currency") or "$"
                total_rewards[currency] = total_rewards.get(currency, 0) + int(r["reward"])
            except (TypeError, ValueError):
                pass

    if total_rewards:
        total_reward = "，".join(
            quota_to_currency(total, currency) for currency, total in total_rewards.items()
        )
    else:
        total_reward = quota_to_currency(0)

    return f"""
<h2>📋 签到日报 {now}</h2>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>平台</th><th>状态</th><th>今日奖励</th><th>当前余额</th><th>备注</th></tr>
{rows}
</table>
<p>💰 今日总奖励: <strong>{total_reward}</strong></p>
"""


def send_pushplus(title: str, content: str) -> None:
    if not PUSHPLUS_TOKEN:
        print("未配置 PUSHPLUS_TOKEN，跳过推送")
        return
    try:
        response = requests.post(
            "https://www.pushplus.plus/send",
            json={"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "html"},
            impersonate="chrome124",
            timeout=30,
        )
        response.raise_for_status()
        print(f"PushPlus 推送成功: {response.text[:200]}")
    except Exception as exc:
        print(f"PushPlus 推送失败: {exc}", file=sys.stderr)


def main() -> int:
    results = []
    for name, module_path in PLATFORMS:
        r = run_platform(name, module_path)
        results.append(r)

    html = build_html(results)
    print("\n" + "=" * 40)
    print("📊 签到汇总")
    print("=" * 40)
    for r in results:
        if r.get("skipped"):
            continue
        s = "✅" if r.get("success") else "❌"
        currency = r.get("currency") or "$"
        reward = quota_to_currency(r.get("reward"), currency)
        balance = quota_to_currency(r.get("balance"), currency)
        print(f"  {s} {r['platform']}: 奖励={reward} 余额={balance}  {r.get('message', '')}")

    send_pushplus("多平台签到日报", html)
    failed = [r for r in results if not r.get("success") and not r.get("skipped")]
    return len(failed)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    raise SystemExit(main())
