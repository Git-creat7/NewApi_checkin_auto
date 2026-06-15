
#!/usr/bin/env python3
import os
import sys

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from curl_cffi import requests


BASE_URL = os.getenv("SUB2_BASE_URL", "https://sub.100xlabs.space").rstrip("/")
ACCESS_TOKEN = os.getenv("SUB2_ACCESS_TOKEN", "").strip()
API_USER = os.getenv("SUB2_API_USER", "").strip()
TIMEOUT = int(os.getenv("SUB2_TIMEOUT", "30"))


class ApiError(RuntimeError):
    pass


def make_session() -> requests.Session:
    if not ACCESS_TOKEN:
        raise ApiError("SUB2_ACCESS_TOKEN is required.")

    session = requests.Session(impersonate="chrome124", timeout=TIMEOUT)
    session.headers.update(
        {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/dashboard",
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


def post_checkin(session: requests.Session) -> dict:
    return ensure_json(session.post(f"{BASE_URL}/api/v1/check-in"), "签到")


def main() -> int:
    session = make_session()

    result = post_checkin(session)
    user_id = result.get("id")
    email = result.get("email")
    balance = result.get("balance")
    message = result.get("message") or result.get("msg") or ""
    success = bool(user_id) or bool(result.get("success"))

    if API_USER and str(user_id) != API_USER:
        raise ApiError(f"返回用户 id={user_id} 与配置的 SUB2_API_USER={API_USER} 不一致。")

    if not success:
        if "already" in message.lower() or "已经签到" in message or "已签到" in message:
            print(f"✅ 今日已签到: {message}")
            return 0
        raise ApiError(message or "Check-in failed.")

    print(f"当前账号: id={user_id} email={email}")
    if balance is not None:
        print(f"✅ 签到成功！当前余额={balance}")
    else:
        print(f"✅ 签到成功: {message or result}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
