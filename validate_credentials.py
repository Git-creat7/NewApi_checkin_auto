#!/usr/bin/env python3
import importlib
import os
import sys
import time

from checkin_all import PLATFORMS, send_pushplus, quota_to_currency


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def has_creds(name: str) -> bool:
    env_prefix = name.upper().replace("-", "_")
    return bool(
        os.getenv(f"{env_prefix}_ACCESS_TOKEN", "")
        or os.getenv(f"{env_prefix}_SESSION", "")
        or os.getenv(f"{env_prefix}_COOKIE", "")
    )


def validate_platform(name: str, module_path: str) -> dict:
    started = time.monotonic()
    if not has_creds(name):
        return {
            "platform": name,
            "success": True,
            "message": "未配置凭据，跳过",
            "skipped": True,
            "duration": 0.0,
        }

    try:
        mod = importlib.import_module(module_path)
        if hasattr(mod, "validate"):
            result = mod.validate()
        else:
            session = mod.make_session()
            user = mod.fetch_self(session)
            result = {
                "platform": "Boxying",
                "success": True,
                "message": f"id={user.get('id')} name={user.get('display_name')}",
                "balance": user.get("quota"),
            }
        result["duration"] = round(time.monotonic() - started, 2)
        return result
    except Exception as exc:
        return {
            "platform": name,
            "success": False,
            "message": str(exc),
            "error_type": type(exc).__name__,
            "duration": round(time.monotonic() - started, 2),
        }


def build_report(results: list[dict]) -> str:
    rows = []
    for result in results:
        if result.get("skipped"):
            continue
        status = "✅" if result.get("success") else "❌"
        currency = result.get("currency") or "$"
        balance = quota_to_currency(result.get("balance"), currency)
        detail = result.get("message", "")
        if result.get("error_type"):
            detail = f"{result.get('error_type')}: {detail}"
        rows.append(
            f"{status} {result.get('platform')}: 余额={balance} "
            f"耗时={float(result.get('duration') or 0):.2f}s {detail}"
        )

    finished = [r for r in results if not r.get("skipped")]
    ok_count = len([r for r in finished if r.get("success")])
    failed_count = len([r for r in finished if not r.get("success")])
    skipped_count = len([r for r in results if r.get("skipped")])
    return "\n".join(
        [f"凭据校验：完成 {ok_count}，失败 {failed_count}，跳过 {skipped_count}", *rows]
    )


def main() -> int:
    results = [validate_platform(name, module_path) for name, module_path in PLATFORMS]
    report = build_report(results)
    print(report)
    failed = [r for r in results if not r.get("success") and not r.get("skipped")]
    title = "多平台凭据校验"
    if failed:
        title += "：有失败"
    send_pushplus(title, report.replace("\n", "<br>"))
    return len(failed)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    raise SystemExit(main())
