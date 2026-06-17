
#!/usr/bin/env python3
import os
import sys
import json
import time

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright


BASE_URL = os.getenv("ANYROUTER_BASE_URL", "https://anyrouter.top").rstrip("/")
COOKIE = os.getenv("ANYROUTER_COOKIE", "").strip()
API_USER = os.getenv("ANYROUTER_API_USER", "").strip()
TIMEOUT = int(os.getenv("ANYROUTER_TIMEOUT", "60"))


class ApiError(RuntimeError):
    pass


def parse_cookie_string(cookie_str: str, domain: str):
    cookies = []
    for item in cookie_str.split(";"):
        item = item.strip()
        if not item or "=" not in item:
            continue
        name, value = item.split("=", 1)
        cookies.append(
            {
                "name": name.strip(),
                "value": value.strip(),
                "domain": domain.lstrip("https://").lstrip("http://").split(":")[0],
                "path": "/",
            }
        )
    return cookies


def ensure_json(text: str, label: str) -> dict:
    try:
        data = json.loads(text)
    except Exception as exc:
        raise ApiError(f"{label}: invalid JSON - {text[:200]}") from exc
    print(f"{label}: {text[:300]}")
    return data


def main() -> dict:
    result = {"platform": "AnyRouter", "success": False, "message": "", "reward": None, "balance": None}
    if not COOKIE:
        raise ApiError("ANYROUTER_COOKIE is required.")
    if not API_USER:
        raise ApiError("ANYROUTER_API_USER is required.")

    domain = BASE_URL.lstrip("https://").lstrip("http://").split(":")[0]
    cookies = parse_cookie_string(COOKIE, domain)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
            ),
            viewport={"width": 390, "height": 844},
        )
        context.add_cookies(cookies)
        page = context.new_page()

        print("正在访问 AnyRouter 主页，等待 WAF 挑战完成...")
        page.goto(BASE_URL, timeout=TIMEOUT * 1000, wait_until="networkidle")
        time.sleep(5)

        print("正在请求用户信息...")
        page.set_extra_http_headers({"new-api-user": API_USER})
        page.goto(
            f"{BASE_URL}/api/user/self",
            timeout=TIMEOUT * 1000,
            wait_until="networkidle",
        )
        body = page.locator("body").inner_text()

        data = ensure_json(body, "用户信息")
        if not data.get("success"):
            raise ApiError(data.get("message") or "Authentication failed.")

        user = data.get("data") or {}
        print(f"当前账号: id={user.get('id')} name={user.get('display_name')}")

        if str(user.get("id")) != API_USER:
            raise ApiError(
                f"返回用户 id={user.get('id')} 与配置的 ANYROUTER_API_USER={API_USER} 不一致。"
            )

        result["success"] = True
        result["balance"] = user.get("quota")
        result["message"] = "登录成功"
        print("✅ 登录成功（AnyRouter 只需保持登录即可）")

        browser.close()
    return result


if __name__ == "__main__":
    try:
        r = main()
        raise SystemExit(0 if r["success"] else 1)
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
