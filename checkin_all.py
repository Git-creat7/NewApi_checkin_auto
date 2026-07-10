#!/usr/bin/env python3
import os
import sys
import importlib
import time
from datetime import datetime, timezone
from html import escape

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from curl_cffi import requests

from checkin.token_site import quota_to_currency


PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "").strip()


PLATFORMS = [
    ("boxying", "checkin.boxying.checkin"),
    ("elysiver", "checkin.elysiver.checkin"),
    ("n1neman", "checkin.n1neman.checkin"),
    ("jiuuij", "checkin.jiuuij.checkin"),
    ("muyuan", "checkin.muyuan.checkin"),
    ("r91", "checkin.7rfit.checkin"),
    ("maoyulin", "checkin.maoyulin.checkin"),
    ("chy", "checkin.chy.checkin"),
    ("mofas", "checkin.mofas.checkin"),
    ("venlacy", "checkin.venlacy.checkin"),
    ("cun", "checkin.cun.checkin"),
]


def run_platform(name: str, module_path: str) -> dict:
    started = time.monotonic()
    env_prefix = name.upper().replace("-", "_")
    has_creds = bool(os.getenv(f"{env_prefix}_ACCESS_TOKEN", "") or os.getenv(f"{env_prefix}_SESSION", "") or os.getenv(f"{env_prefix}_COOKIE", ""))
    if not has_creds:
        print(f"\n⏭️ {name}: 未配置凭据，跳过")
        return {"platform": name, "success": True, "message": "未配置凭据，跳过", "reward": None, "balance": None, "skipped": True, "duration": 0.0}

    print(f"\n{'='*40}")
    print(f"▶ 开始签到: {name}")
    print(f"{'='*40}")
    try:
        mod = importlib.import_module(module_path)
        result = mod.main()
        result["duration"] = round(time.monotonic() - started, 2)
        return result
    except Exception as exc:
        print(f"❌ {name} 签到异常: {exc}")
        return {
            "platform": name,
            "success": False,
            "message": str(exc),
            "reward": None,
            "balance": None,
            "duration": round(time.monotonic() - started, 2),
            "error_type": type(exc).__name__,
        }


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
        duration = f"{float(r.get('duration') or 0):.2f}s"
        msg = r.get("message", "")
        if r.get("error_type"):
            msg = f"{r.get('error_type')}: {msg}"
        rows += (
            f"<tr><td>{escape(str(platform))}</td><td>{status}</td>"
            f"<td>{escape(reward)}</td><td>{escape(balance)}</td>"
            f"<td>{escape(duration)}</td><td>{escape(str(msg))}</td></tr>"
        )

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

    finished = [r for r in results if not r.get("skipped")]
    ok_count = len([r for r in finished if r.get("success")])
    failed_count = len([r for r in finished if not r.get("success")])
    skipped_count = len([r for r in results if r.get("skipped")])
    total_duration = sum(float(r.get("duration") or 0) for r in results)

    return f"""
<h2>📋 签到日报 {now}</h2>
<p>完成 {ok_count}，失败 {failed_count}，跳过 {skipped_count}，耗时 {total_duration:.2f}s</p>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>平台</th><th>状态</th><th>今日奖励</th><th>当前余额</th><th>耗时</th><th>备注</th></tr>
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
        duration = f"{float(r.get('duration') or 0):.2f}s"
        detail = r.get("message", "")
        if r.get("error_type"):
            detail = f"{r.get('error_type')}: {detail}"
        print(f"  {s} {r['platform']}: 奖励={reward} 余额={balance} 耗时={duration}  {detail}")

    failed = [r for r in results if not r.get("success") and not r.get("skipped")]
    title = "多平台签到日报"
    if failed:
        title += "：有失败"
    send_pushplus(title, html)
    return len(failed)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    raise SystemExit(main())
