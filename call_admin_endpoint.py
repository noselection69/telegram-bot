#!/usr/bin/env python3
"""
Помощник для вызова admin endpoint на Railway
Использование:
    python call_admin_endpoint.py https://your-railway-app.railway.app
"""
import sys
import requests
import json

if len(sys.argv) < 2:
    print("❌ Usage: python call_admin_endpoint.py <base_url>")
    print("Example: python call_admin_endpoint.py https://your-app.railway.app")
    sys.exit(1)

base_url = sys.argv[1].rstrip('/')
endpoint = f"{base_url}/api/admin/reset-bp-tasks"
admin_key = "gta5rp_admin_2024"

print(f"🔄 Calling admin endpoint: {endpoint}")
print(f"📋 Admin Key: {admin_key}")
print("=" * 80)

try:
    response = requests.post(
        endpoint,
        headers={"X-Admin-Key": admin_key},
        timeout=30
    )
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📝 Response Headers: {dict(response.headers)}")
    print(f"\n📋 Response Body:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("\n✅ BP tasks successfully reset!")
    elif response.status_code == 403:
        print("\n❌ ERROR: Unauthorized! Check admin key.")
    else:
        print(f"\n❌ ERROR: Unexpected status code {response.status_code}")

except requests.exceptions.Timeout:
    print("\n❌ ERROR: Request timeout! Check if the app is running.")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ ERROR: Connection failed! {e}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
