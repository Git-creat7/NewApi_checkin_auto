#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timezone

from curl_cffi import requests


BASE_URL = os.getenv("XEM_BASE_URL", "http://new.xem8k5.top:3000/").rstrip("/")
SESSION = os.getenv("XEM_SESSION", "").strip()
API_USER = os.getenv("XEM_API_USER", "").strip()
# 推送环境变量
PUSH_KEY = os.getenv("PUSH_KEY", "").strip()
TIMEOUT = int(os.getenv("XEM_TIMEOUT", "30"))
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "").strip()


class ApiError(RuntimeError):
    pass


def send_pushplus(title: str, content: str) -> None:
    if not PUSHPLUS_TOKEN:
        return

    try:
        response = requests.post(
            "https://www.pushplus.plus/send",
            json={
                "token": PUSHPLUS_TOKEN,
                "title": title,
                "content": content,
                "template": "markdown",
            },
            impersonate="chrome124",
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        print(f"PushPlus response: {response.text[:300]}")
    except Exception as exc:
        print(f"PushPlus send failed: {exc}", file=sys.stderr)


def current_month() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m")


def current_day() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def make_session(include_api_user: bool = True) -> requests.Session:
    if not SESSION:
        raise ApiError("XEM_SESSION is required.")

    session = requests.Session(impersonate="chrome124", timeout=TIMEOUT)
    session.cookies.set("session", SESSION, domain="www.xem8k5.top")
    session.headers.update(
        {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/console",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Cookie": f"session={SESSION}",
        }
    )
    if include_api_user and API_USER:
        session.headers["new-api-user"] = API_USER
    return session


def ensure_json_response(response, label: str) -> dict:
    try:
        data = response.json()
    except Exception as exc:
        raise ApiError(f"{label} returned invalid JSON: {response.text[:200]}") from exc
    print(f"{label}: {response.text[:300]}")
    return data


def fetch_site_status(session: requests.Session) -> dict:
    response = session.get(f"{BASE_URL}/api/status")
    data = ensure_json_response(response, "站点状态响应")
    if not data.get("success"):
        raise ApiError(data.get("message") or "Failed to fetch site status.")
    return data.get("data") or {}


def fetch_self(session: requests.Session) -> dict:
    response = session.get(f"{BASE_URL}/api/user/self")
    data = ensure_json_response(response, "用户信息响应")
    if not data.get("success"):
        raise ApiError(data.get("message") or "Authentication failed.")

    user = data.get("data") or {}
    actual_id = str(user.get("id", "")).strip()
    if API_USER and actual_id and API_USER != actual_id:
        raise ApiError(
            f"XEM_API_USER={API_USER} 与当前登录账号 id={actual_id} 不一致，请改成 {actual_id}。"
        )
    return user


def fetch_checkin_status(session: requests.Session) -> dict:
    response = session.get(f"{BASE_URL}/api/user/checkin")
    # 典型返回: {"success":true, "message":"...", "data": 100}
    # 或者返回是否可以签到的布尔值
    return ensure_json_response(response, "XEM 签到状态响应")


def post_checkin(session: requests.Session, status: dict | None = None) -> dict:
    # 经典路径通常不需要 seed/proof，直接 POST 即可
    response = session.post(f"{BASE_URL}/api/user/checkin")
    return ensure_json_response(response, "XEM 签到动作响应")


def extract_stats(status: dict) -> dict:
    return ((status.get("data") or {}).get("stats") or {})


def extract_today_reward(status: dict) -> int | None:
    today = current_day()
    stats = extract_stats(status)
    records = stats.get("records") or []
    for record in records:
        if record.get("checkin_date") == today:
            try:
                return int(record.get("quota_awarded"))
            except (TypeError, ValueError):
                return None
    return None


def run_once(include_api_user: bool) -> int:
    session = make_session(include_api_user=include_api_user)

    site_status = fetch_site_status(session)
    if not site_status.get("checkin_enabled"):
        print("ℹ️ 签到功能未开启")
        return 0
    if site_status.get("turnstile_check"):
        print("⚠️ 站点启用了 Turnstile，继续尝试使用现有 session 签到...")

    user = fetch_self(session)
    print(f"当前账号: id={user.get('id')} display_name={user.get('display_name')}")

    status = fetch_checkin_status(session)
    if status.get("success"):
        data = status.get("data") or {}
        stats = data.get("stats") or {}
        if stats.get("checked_in_today"):
            print(
                f"✅ 今日已签到，累计={stats.get('total_checkins')}，总额度={stats.get('total_quota')/500000}"
            )
            return 0
        if data.get("can_checkin") is False:
            raise ApiError(
                f"当前账号未达到签到门槛: current_topup_amount={data.get('current_topup_amount')} "
                f"min_topup_amount={data.get('min_topup_amount')}"
            )
    before_total_quota = extract_stats(status).get("total_quota")

    result = post_checkin(session, status=status)
    message = result.get("message") or result.get("msg") or ""
    success = bool(result.get("success") or result.get("ret") == 1)

    if not success and ("已经签到" in message or "已签到" in message):
        print(f"✅ 今日已签到: {message}")
        return 0

    if not success and "turnstile" in message.lower():
        raise ApiError(f"签到失败，需要 Turnstile 验证: {message}")

    if not success:
        raise ApiError(message or "Check-in failed.")

    refreshed_status = fetch_checkin_status(session)
    after_stats = extract_stats(refreshed_status)
    today_awarded = extract_today_reward(refreshed_status)
    after_total_quota = after_stats.get("total_quota")

    if today_awarded is None:
        try:
            if before_total_quota is not None and after_total_quota is not None:
                today_awarded = int(after_total_quota) - int(before_total_quota)
        except (TypeError, ValueError):
            today_awarded = None

    if today_awarded is not None:
        print(
            f"✅ 签到成功！今日奖励={today_awarded}，累计签到={after_stats.get('total_checkins')}，累计获得={after_total_quota}"
        )
    else:
        print(f"✅ 签到成功: {message or result}")
    return 0


def main() -> int:
    try:
        code = run_once(include_api_user=True)
        send_pushplus(
            "XEM 签到结果",
            f"### XEM 签到成功\n\n- 站点: `{BASE_URL}`\n- 时间: `{current_day()}`",
        )
        return code
    except ApiError as exc:
        msg = str(exc)
        if API_USER and "insufficient privileges" in msg.lower():
            print("⚠️ 使用 new-api-user 头失败，尝试仅凭 session 重试一次...")
            code = run_once(include_api_user=False)
            send_pushplus(
                "XEM 签到结果",
                f"### XEM 签到成功\n\n- 站点: `{BASE_URL}`\n- 时间: `{current_day()}`\n- 备注: `new-api-user` 回退为仅使用 session",
            )
            return code
        send_pushplus(
            "XEM 签到失败",
            f"### XEM 签到失败\n\n- 站点: `{BASE_URL}`\n- 时间: `{current_day()}`\n- 错误: `{msg}`",
        )
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
