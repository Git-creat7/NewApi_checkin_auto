
#!/usr/bin/env python3
import os
import sys

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from curl_cffi import requests


BASE_URL = os.getenv("ANYROUTER_BASE_URL", "https://anyrouter.top").rstrip("/")
COOKIE = os.getenv("ANYROUTER_COOKIE", "").strip()
API_USER = os.getenv("ANYROUTER_API_USER", "").strip()
TIMEOUT = int(os.getenv("ANYROUTER_TIMEOUT", "30"))


class ApiError(RuntimeError):
    pass


def make_session() -> requests.Session:
    if not COOKIE:
        raise ApiError("ANYROUTER_COOKIE is required.")
    if not API_USER:
        raise ApiError("ANYROUTER_API_USER is required.")

    session = requests.Session(impersonate="chrome124", timeout=TIMEOUT)
    session.headers.update(
        {
            "Accept": "application/json, text/plain, */*",
            "Cookie": COOKIE,
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


def main() -> int:
    session = make_session()

    user = fetch_self(session)
    print(f"当前账号: id={user.get('id')} name={user.get('display_name')}")
    print("✅ 登录成功（AnyRouter 只需保持登录即可）")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
