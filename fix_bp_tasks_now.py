#!/usr/bin/env python3
"""
РЕШЕНИЕ: Принудительное обновление BP tasks на Railway
Используйте этот скрипт чтобы вызвать admin endpoint
"""
import requests
import json
import sys

# УКАЖИТЕ ЗДЕСЬ ВАШ URL RAILWAY ПРИЛОЖЕНИЯ
RAILWAY_APP_URL = input("Введите URL вашего приложения на Railway (например: https://gta5bot-prod.railway.app): ").strip().rstrip('/')

if not RAILWAY_APP_URL.startswith('http'):
    RAILWAY_APP_URL = 'https://' + RAILWAY_APP_URL

ADMIN_ENDPOINT = f"{RAILWAY_APP_URL}/api/admin/reset-bp-tasks"
ADMIN_KEY = "gta5rp_admin_2024"

print(f"\n🔄 Calling admin endpoint to force BP tasks reset...")
print(f"   URL: {ADMIN_ENDPOINT}")
print(f"   Admin Key: {ADMIN_KEY}")
print("=" * 80)

try:
    response = requests.post(
        ADMIN_ENDPOINT,
        headers={"X-Admin-Key": ADMIN_KEY},
        timeout=30
    )
    
    print(f"\n📊 Response Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS!")
        print(f"   Message: {data.get('message', 'Unknown')}")
        print(f"   Tasks added: {data.get('added', 'Unknown')}")
        print("\n🎉 BP tasks have been successfully reset to 59 items!")
    elif response.status_code == 403:
        print(f"❌ ERROR: Unauthorized (403)")
        print(f"   Check if admin key is correct: {ADMIN_KEY}")
    else:
        print(f"❌ ERROR: Unexpected status code {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    
    print(f"\n📋 Full response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
except requests.exceptions.Timeout:
    print("❌ ERROR: Request timeout!")
    print("   Check if Railway app is running")
    print("   Check if you have internet connection")
    sys.exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"❌ ERROR: Connection failed!")
    print(f"   Details: {e}")
    print("   Check if URL is correct")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("Проверьте что BP tasks обновились через web interface или API")
