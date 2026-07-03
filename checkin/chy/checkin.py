#!/usr/bin/env python3
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from checkin.token_site import (
    ApiError,
    TokenSiteConfig,
    fetch_self,
    make_session,
    post_checkin,
    validate_token_site,
)


CONFIG = TokenSiteConfig(
    platform="CHY公益站",
    env_prefix="CHY",
    default_base_url="https://chybenzun.top",
)


def main() -> dict:
    result = {
        "platform": CONFIG.platform,
        "success": False,
        "message": "",
        "reward": None,
        "balance": None,
        "currency": CONFIG.currency,
    }
    session = make_session(CONFIG)

    try:
        user_before = fetch_self(CONFIG, session)
    except ApiError as exc:
        if os.getenv("GITHUB_ACTIONS") == "true" and "Just a moment" in str(exc):
            result["success"] = True
            result["message"] = "GitHub Actions 被 Cloudflare challenge 拦截，已跳过"
            print(f"⏭️ {result['message']}")
            return result
        raise

    print(f"当前账号: id={user_before.get('id')} name={user_before.get('display_name')}")
    result["balance"] = user_before.get("quota")

    checkin_resp = post_checkin(CONFIG, session)
    message = checkin_resp.get("message") or checkin_resp.get("msg") or ""
    success = bool(checkin_resp.get("success") or checkin_resp.get("ret") == 1)

    already = not success and ("已经签到" in message or "已签到" in message)
    if already:
        result["success"] = True
        result["message"] = message
        print(f"✅ 今日已签到: {message}")
        return result

    if not success:
        raise ApiError(message or "Check-in failed.")

    user_after = fetch_self(CONFIG, session)
    result["balance"] = user_after.get("quota")

    data = checkin_resp.get("data")
    if isinstance(data, dict) and data.get("points_awarded") is not None:
        result["success"] = True
        result["message"] = f"签到成功，今日奖励={data.get('points_awarded')} 积分"
        print(f"✅ {result['message']}")
        return result

    reward = data.get("quota_awarded") if isinstance(data, dict) else data
    try:
        result["reward"] = int(reward) if reward is not None else None
    except (TypeError, ValueError):
        result["reward"] = None
    result["success"] = True
    result["message"] = message or "签到成功"
    print(f"✅ {result['message']}")
    return result


def validate() -> dict:
    return validate_token_site(CONFIG)


if __name__ == "__main__":
    try:
        r = main()
        raise SystemExit(0 if r["success"] else 1)
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
