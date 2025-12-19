#!/usr/bin/env python3
"""Диагностика переменных окружения и конфига"""
import os

print("=" * 60)
print("🔍 ДИАГНОСТИКА БОТА")
print("=" * 60)

print("\n📌 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
print(f"BOT_TOKEN: {'SET' if os.getenv('BOT_TOKEN') else 'NOT SET'}")
print(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
print(f"WEB_APP_URL: {os.getenv('WEB_APP_URL', 'NOT SET')}")
print(f"WEBHOOK_URL: {os.getenv('WEBHOOK_URL', 'NOT SET')}")
print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
print(f"PORT: {os.getenv('PORT', 'NOT SET')}")

print("\n🔐 КОНСТАНТЫ:")
print(f"ADMIN_ID: 360028214")
print(f"FALLBACK WEB_APP_URL: https://web-production-70ac2.up.railway.app")

print("\n✅ ИСПОЛЬЗУЕМЫЕ URLs:")
web_app_url = os.getenv('WEB_APP_URL', 'https://web-production-70ac2.up.railway.app')
webhook_url = os.getenv('WEB_APP_URL') or os.getenv('WEBHOOK_URL', 'https://web-production-70ac2.up.railway.app')
print(f"В main.py (set_menu_button): {web_app_url}")
print(f"В keyboards.py (WEBHOOK_URL): {webhook_url}")

print("\n" + "=" * 60)
print("✅ Диагностика завершена")
print("=" * 60)
