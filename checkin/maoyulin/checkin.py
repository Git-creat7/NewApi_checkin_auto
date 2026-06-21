#!/usr/bin/env python3
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from curl_cffi import requests


BASE_URL = os.getenv("MAOYULIN_BASE_URL", "https://maoyulin.xyz").rstrip("/")
ACCESS_TOKEN = os.getenv("MAOYULIN_ACCESS_TOKEN", "").strip()
API_USER = os.getenv("MAOYULIN_API_USER", "").strip()
TIMEOUT = int(os.getenv("MAOYULIN_TIMEOUT", "30"))
CURRENCY = os.getenv("MAOYULIN_CURRENCY", "猫猫").strip() or "猫猫"


class ApiError(RuntimeError):
    pass


def make_session() -> requests.Session:
    if not ACCESS_TOKEN:
        raise ApiError("MAOYULIN_ACCESS_TOKEN is required.")
    if not API_USER:
        raise ApiError("MAOYULIN_API_USER is required.")

    session = requests.Session(impersonate="chrome124", timeout=TIMEOUT)
    session.headers.update(
        {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "new-api-user": API_USER,
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/console",
        }
    )
    return session


def ensure_json(response, label: str) -> dict:
    try:
        data = response.json()
    except Exception as exc:
        raise ApiError(f"{label}: invalid JSON - {response.text[:200]}") from exc
    print(f"{label}: {response.text[:300]}")
    return data


def fetch_self(session: requests.Session) -> dict:
    data = ensure_json(session.get(f"{BASE_URL}/api/user/self"), "用户信息")
    if not data.get("success"):
        raise ApiError(data.get("message") or "Authentication failed.")
    return data.get("data") or {}


def post_checkin(session: requests.Session) -> dict:
    return ensure_json(session.post(f"{BASE_URL}/api/user/checkin"), "签到")


def quota_to_currency(quota) -> str:
    if quota is None:
        return "-"
    try:
        amount = int(quota) / 500000
    except (TypeError, ValueError):
        return str(quota)
    if CURRENCY == "$":
        return f"${amount:.2f}"
    return f"{amount:.2f} {CURRENCY}"


def main() -> dict:
    result = {
        "platform": "Maoyulin",
        "success": False,
        "message": "",
        "reward": None,
        "balance": None,
        "currency": CURRENCY,
    }
    session = make_session()

    user_before = fetch_self(session)
    print(f"当前账号: id={user_before.get('id')} name={user_before.get('display_name')}")
    quota_before = user_before.get("quota")

    checkin_resp = post_checkin(session)
    message = checkin_resp.get("message") or checkin_resp.get("msg") or ""
    success = bool(checkin_resp.get("success") or checkin_resp.get("ret") == 1)

    already = not success and ("已经签到" in message or "已签到" in message)
    if already:
        result["success"] = True
        result["balance"] = quota_before
        result["message"] = message
        print(f"✅ 今日已签到: {message}")
        return result

    if not success:
        raise ApiError(message or "Check-in failed.")

    user_after = fetch_self(session)
    quota_after = user_after.get("quota")

    reward_from_api = checkin_resp.get("data")
    if reward_from_api is not None:
        try:
            reward_from_api = int(reward_from_api)
        except (TypeError, ValueError):
            reward_from_api = None

    reward_diff = None
    if quota_before is not None and quota_after is not None:
        try:
            reward_diff = int(quota_after) - int(quota_before)
        except (TypeError, ValueError):
            reward_diff = None

    reward = reward_from_api if reward_from_api is not None else reward_diff
    result["success"] = True
    result["reward"] = reward
    result["balance"] = quota_after
    if reward is not None:
        formatted_reward = quota_to_currency(reward)
        print(f"✅ 签到成功！今日奖励={formatted_reward}")
        result["message"] = f"签到成功，今日奖励={formatted_reward}"
    else:
        print(f"✅ 签到成功: {message or checkin_resp}")
        result["message"] = message or "签到成功"
    return result


if __name__ == "__main__":
    try:
        r = main()
        raise SystemExit(0 if r["success"] else 1)
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
