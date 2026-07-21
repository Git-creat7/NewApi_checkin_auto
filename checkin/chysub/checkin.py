#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from urllib.parse import parse_qs, unquote, urlparse

from curl_cffi import requests


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


PLATFORM = "CHY订阅"
ENV_PREFIX = "CHYSUB"
DEFAULT_BASE_URL = "https://dy.chybenzun.top"
CURRENCY = "GB"


class ApiError(RuntimeError):
    pass


def site_env() -> tuple[str, str, int]:
    base_url = os.getenv(f"{ENV_PREFIX}_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    timeout = int(os.getenv(f"{ENV_PREFIX}_TIMEOUT", "30"))
    cookie = os.getenv(f"{ENV_PREFIX}_COOKIE", "").strip()
    if not cookie:
        session = os.getenv(f"{ENV_PREFIX}_SESSION", "").strip()
        cf_clearance = os.getenv(f"{ENV_PREFIX}_CF_CLEARANCE", "").strip()
        imt = os.getenv(f"{ENV_PREFIX}_IMT_HANDSHAKE", "").strip()
        parts = []
        if cf_clearance:
            parts.append(f"cf_clearance={cf_clearance}")
        if session:
            parts.append(f"chy_session={session}")
        if imt:
            parts.append(f"__imt_handshake_page_id={imt}")
        cookie = "; ".join(parts)
    return base_url, cookie, timeout


def make_session() -> requests.Session:
    base_url, cookie, timeout = site_env()
    if not cookie:
        raise ApiError(
            f"{ENV_PREFIX}_COOKIE 或 {ENV_PREFIX}_SESSION+{ENV_PREFIX}_CF_CLEARANCE 必填。"
        )
    if "chy_session=" not in cookie and not os.getenv(f"{ENV_PREFIX}_SESSION", "").strip():
        raise ApiError(f"Cookie 中缺少 chy_session，请检查 {ENV_PREFIX}_COOKIE / {ENV_PREFIX}_SESSION。")

    session = requests.Session(impersonate="chrome124", timeout=timeout)
    session.headers.update(
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Cookie": cookie,
            "Origin": base_url,
            "Referer": f"{base_url}/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
    )
    return session


def parse_stats(html: str) -> dict:
    stats = {}
    for value, label in re.findall(
        r'class="v">\s*([^<]+?)\s*</div>\s*<div class="l">\s*([^<]+?)\s*</div>',
        html,
    ):
        stats[label.strip()] = value.strip()

    name = None
    m = re.search(r'class="name"[^>]*>\s*([^<]+)', html)
    if m:
        name = m.group(1).strip()
    if not name:
        m = re.search(r">(NeoCreat|LINUXDO[^<]*)<", html)
        if m:
            name = m.group(1).strip()

    remaining = stats.get("剩余") or stats.get("剩餘")
    total = stats.get("总额度") or stats.get("總額度") or stats.get("总配额")
    used = stats.get("已使用")

    return {
        "name": name,
        "remaining": remaining,
        "total": total,
        "used": used,
        "stats": stats,
    }


def is_cloudflare_block(status: int, html: str) -> bool:
    if status in (403, 503):
        return True
    lowered = (html or "").lower()
    return (
        "just a moment" in (html or "")
        or "cf-browser-verification" in lowered
        or "cdn-cgi/challenge-platform" in lowered
        or "attention required" in lowered
    )


def fetch_home(session: requests.Session) -> tuple[str, dict]:
    base_url, _, _ = site_env()
    response = session.get(f"{base_url}/", allow_redirects=True)
    html = response.text or ""
    if is_cloudflare_block(response.status_code, html):
        raise ApiError("被 Cloudflare challenge 拦截，请更新 cf_clearance。")
    if response.status_code >= 400:
        raise ApiError(f"首页请求失败: HTTP {response.status_code}")
    if 'href="/logout"' not in html and "退出" not in html:
        if "/claim" not in html and "领取" not in html:
            raise ApiError("未登录或 Cookie 失效（首页无签到入口）。")
    return html, parse_stats(html)


def claim_message(location: str | None, final_url: str) -> str:
    for candidate in (location, final_url):
        if not candidate:
            continue
        query = parse_qs(urlparse(candidate).query)
        msgs = query.get("msg") or []
        if msgs:
            return unquote(msgs[0])
    return ""


def post_claim(session: requests.Session) -> tuple[int, str]:
    base_url, _, _ = site_env()
    response = session.get(f"{base_url}/claim", allow_redirects=False)
    if response.status_code in (301, 302, 303, 307, 308):
        location = response.headers.get("Location") or ""
        if location.startswith("/"):
            location = base_url + location
        msg = claim_message(location, location)
        return response.status_code, msg

    response = session.get(f"{base_url}/claim", allow_redirects=True)
    msg = claim_message(None, str(response.url))
    if not msg and response.text:
        m = re.search(r"[?&]msg=([^&\"']+)", response.text)
        if m:
            msg = unquote(m.group(1))
    return response.status_code, msg


def main() -> dict:
    result = {
        "platform": PLATFORM,
        "success": False,
        "message": "",
        "reward": None,
        "balance": None,
        "currency": CURRENCY,
    }
    session = make_session()
    try:
        html, stats = fetch_home(session)
    except ApiError as exc:
        if os.getenv("GITHUB_ACTIONS") == "true" and "Cloudflare" in str(exc):
            result["success"] = True
            result["message"] = "GitHub Actions 被 Cloudflare challenge 拦截，已跳过"
            print(f"⏭️ {result['message']}")
            return result
        raise

    if stats.get("name"):
        print(f"当前账号: {stats['name']}")
    if stats.get("remaining"):
        result["balance"] = stats["remaining"]
        print(
            f"额度: 总={stats.get('total') or '-'} 已用={stats.get('used') or '-'} "
            f"剩余={stats.get('remaining')}"
        )

    status, msg = post_claim(session)
    print(f"领取响应: HTTP {status} msg={msg or '-'}")

    already = any(k in msg for k in ("今日已领取", "已领取过", "已经领取", "已签到", "已经签到"))
    success_like = any(k in msg for k in ("成功", "领取成功", "已到账", "奖励"))
    if already:
        result["success"] = True
        result["message"] = msg or "今日已领取"
        print(f"✅ {result['message']}")
        return result

    if msg and not already and (success_like or status in (200, 302)):
        try:
            _, after = fetch_home(session)
            if after.get("remaining"):
                result["balance"] = after["remaining"]
        except Exception:
            pass
        reward_m = re.search(r"(\d+(?:\.\d+)?\s*GB)", msg, re.I)
        if not reward_m:
            reward_m = re.search(r"领取每日\s*(\d+(?:\.\d+)?\s*GB)", html)
        if reward_m:
            result["reward"] = reward_m.group(1).replace(" ", "")
        elif "5GB" in html or "5 GB" in html:
            result["reward"] = "5GB"
        result["success"] = True
        result["message"] = msg or "领取成功"
        print(f"✅ {result['message']}")
        return result

    if not msg:
        raise ApiError(f"领取失败: HTTP {status}")
    raise ApiError(msg)


def validate() -> dict:
    session = make_session()
    _, stats = fetch_home(session)
    return {
        "platform": PLATFORM,
        "success": True,
        "message": f"name={stats.get('name') or '?'} remaining={stats.get('remaining') or '-'}",
        "reward": None,
        "balance": stats.get("remaining"),
        "currency": CURRENCY,
    }


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        r = main()
        raise SystemExit(0 if r["success"] else 1)
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
