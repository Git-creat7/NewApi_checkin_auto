#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from curl_cffi import requests


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class ApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class TokenSiteConfig:
    platform: str
    env_prefix: str
    default_base_url: str
    currency: str = "$"


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


def site_env(config: TokenSiteConfig) -> tuple[str, str, str, int, str]:
    prefix = config.env_prefix
    base_url = os.getenv(f"{prefix}_BASE_URL", config.default_base_url).rstrip("/")
    access_token = os.getenv(f"{prefix}_ACCESS_TOKEN", "").strip()
    api_user = os.getenv(f"{prefix}_API_USER", "").strip()
    timeout = int(os.getenv(f"{prefix}_TIMEOUT", "30"))
    currency = os.getenv(f"{prefix}_CURRENCY", config.currency).strip() or config.currency
    return base_url, access_token, api_user, timeout, currency


def make_session(config: TokenSiteConfig) -> requests.Session:
    base_url, access_token, api_user, timeout, _ = site_env(config)
    if not access_token:
        raise ApiError(f"{config.env_prefix}_ACCESS_TOKEN is required.")
    if not api_user:
        raise ApiError(f"{config.env_prefix}_API_USER is required.")

    session = requests.Session(impersonate="chrome124", timeout=timeout)
    session.headers.update(
        {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {access_token}",
            "new-api-user": api_user,
            "Origin": base_url,
            "Referer": f"{base_url}/console",
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


def fetch_self(config: TokenSiteConfig, session: requests.Session) -> dict:
    base_url, _, api_user, _, _ = site_env(config)
    data = ensure_json(session.get(f"{base_url}/api/user/self"), "用户信息")
    if not data.get("success"):
        raise ApiError(data.get("message") or "Authentication failed.")

    user = data.get("data") or {}
    actual_id = str(user.get("id", "")).strip()
    if api_user and actual_id and api_user != actual_id:
        raise ApiError(
            f"{config.env_prefix}_API_USER={api_user} 与当前登录账号 id={actual_id} 不一致，请改成 {actual_id}。"
        )
    return user


def post_checkin(config: TokenSiteConfig, session: requests.Session) -> dict:
    base_url, _, _, _, _ = site_env(config)
    return ensure_json(session.post(f"{base_url}/api/user/checkin"), "签到")


def run_token_checkin(config: TokenSiteConfig) -> dict:
    _, _, _, _, currency = site_env(config)
    result = {
        "platform": config.platform,
        "success": False,
        "message": "",
        "reward": None,
        "balance": None,
        "currency": currency,
    }
    session = make_session(config)

    user_before = fetch_self(config, session)
    print(f"当前账号: id={user_before.get('id')} name={user_before.get('display_name')}")
    quota_before = user_before.get("quota")

    checkin_resp = post_checkin(config, session)
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

    user_after = fetch_self(config, session)
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
        formatted_reward = quota_to_currency(reward, currency)
        print(f"✅ 签到成功！今日奖励={formatted_reward}")
        result["message"] = f"签到成功，今日奖励={formatted_reward}"
    else:
        print(f"✅ 签到成功: {message or checkin_resp}")
        result["message"] = message or "签到成功"
    return result


def run_as_script(config: TokenSiteConfig) -> None:
    try:
        result = run_token_checkin(config)
        raise SystemExit(0 if result["success"] else 1)
    except ApiError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
