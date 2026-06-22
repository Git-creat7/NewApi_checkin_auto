#!/bin/bash
# 设置 GitHub Secrets
# 用法: bash setup-secrets.sh
# 前提: 已安装 gh 并登录 (gh auth login)

set -e

# 检查 gh 是否可用
if ! command -v gh &> /dev/null; then
    echo "请先安装 gh CLI: https://cli.github.com/"
    exit 1
fi

# 检查是否登录
if ! gh auth status &> /dev/null; then
    echo "请先登录: gh auth login"
    exit 1
fi

# ===== Boxying =====
read -p "BOXYING_SESSION: " val
[ -n "$val" ] && gh secret set BOXYING_SESSION -b "$val"

read -p "BOXYING_API_USER: " val
[ -n "$val" ] && gh secret set BOXYING_API_USER -b "$val"

# ===== ELYSIVER =====
read -p "ELYSIVER_ACCESS_TOKEN: " val
[ -n "$val" ] && gh secret set ELYSIVER_ACCESS_TOKEN -b "$val"

read -p "ELYSIVER_API_USER: " val
[ -n "$val" ] && gh secret set ELYSIVER_API_USER -b "$val"

# ===== N1NEMAN =====
read -p "N1NEMAN_ACCESS_TOKEN: " val
[ -n "$val" ] && gh secret set N1NEMAN_ACCESS_TOKEN -b "$val"

read -p "N1NEMAN_API_USER: " val
[ -n "$val" ] && gh secret set N1NEMAN_API_USER -b "$val"

# ===== JIUUIJ =====
read -p "JIUUIJ_ACCESS_TOKEN: " val
[ -n "$val" ] && gh secret set JIUUIJ_ACCESS_TOKEN -b "$val"

read -p "JIUUIJ_API_USER: " val
[ -n "$val" ] && gh secret set JIUUIJ_API_USER -b "$val"

# ===== MUYUAN =====
read -p "MUYUAN_ACCESS_TOKEN: " val
[ -n "$val" ] && gh secret set MUYUAN_ACCESS_TOKEN -b "$val"

read -p "MUYUAN_API_USER: " val
[ -n "$val" ] && gh secret set MUYUAN_API_USER -b "$val"

# ===== 91 =====
read -p "R91_ACCESS_TOKEN: " val
[ -n "$val" ] && gh secret set R91_ACCESS_TOKEN -b "$val"

read -p "R91_API_USER: " val
[ -n "$val" ] && gh secret set R91_API_USER -b "$val"

# ===== MAOYULIN =====
read -p "MAOYULIN_ACCESS_TOKEN: " val
[ -n "$val" ] && gh secret set MAOYULIN_ACCESS_TOKEN -b "$val"

read -p "MAOYULIN_API_USER: " val
[ -n "$val" ] && gh secret set MAOYULIN_API_USER -b "$val"

# ===== 通用推送 =====
read -p "PUSHPLUS_TOKEN (可选): " val
[ -n "$val" ] && gh secret set PUSHPLUS_TOKEN -b "$val"

echo ""
echo "✅ Secrets 设置完成！"
gh secret list
