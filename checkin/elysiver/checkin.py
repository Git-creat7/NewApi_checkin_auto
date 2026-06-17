
# 本地重复签到测试：token测试通过

#!/usr/bin/env python3
import os
import sys

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from curl_cffi import requests


BASE_URL = os.getenv("ELYSIVER_BASE_URL", "https://elysiver.h-e.top").rstrip("/")
ACCESS_TOKEN = os.getenv("ELYSIVER_ACCESS_TOKEN", "").strip()
API_USER = os.getenv("ELYSIVER_API_USER", "").strip()
TIMEOUT = int(os.getenv("ELYSIVER_TIMEOUT", "30"))


class ApiError(RuntimeError):
    pass


def make_session() -> requests.Session:
    if not ACCESS_TOKEN:
        raise ApiError("ELYSIVER_ACCESS_TOKEN is required.")
    if not API_USER:
        raise ApiError("ELYSIVER_API_USER is required.")

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


def main() -> dict:
    result = {"platform": "Elysiver", "success": False, "message": "", "reward": None, "balance": None}
    session = make_session()

    user = fetch_self(session)
    print(f"当前账号: id={user.get('id')} name={user.get('display_name')}")
    result["balance"] = user.get("quota")

    checkin_result = post_checkin(session)
    message = checkin_result.get("message") or checkin_result.get("msg") or ""
    success = bool(checkin_result.get("success") or checkin_result.get("ret") == 1)

    if not success and ("已经签到" in message or "已签到" in message):
        print(f"✅ 今日已签到: {message}")
        result["success"] = True
        result["message"] = message
        return result

    if not success:
        raise ApiError(message or "Check-in failed.")

    reward = checkin_result.get("data")
    if reward is not None:
        try:
            reward = int(reward)
        except (TypeError, ValueError):
            reward = None

    result["success"] = True
    result["reward"] = reward
    if reward is not None:
        print(f"✅ 签到成功！今日奖励={reward}")
        result["message"] = f"签到成功，今日奖励={reward}"
    else:
        print(f"✅ 签到成功: {message or checkin_result}")
        result["message"] = message or "签到成功"
    return result


if __name__ == "__main__":
    try:
        r = main()
        raise SystemExit(0 if r["success"] else 1)
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
