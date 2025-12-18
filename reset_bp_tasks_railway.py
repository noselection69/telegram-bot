#!/usr/bin/env python3
"""
Скрипт для вызова админского эндпоинта сброса BP заданий на Railway
"""
import requests
import sys

# URL твоего бота на Railway
RAILWAY_URL = "https://telegram-bot-production.up.railway.app"
ADMIN_KEY = "gta5rp_admin_2024"

print("=" * 70)
print("🔄 СБРОС BP ЗАДАНИЙ НА RAILWAY")
print("=" * 70)

# Спросим URL если нужно
if len(sys.argv) > 1:
    RAILWAY_URL = sys.argv[1]
else:
    user_url = input("\n📍 Введи URL твоего Railway приложения (или Enter для использования примера): ").strip()
    if user_url:
        RAILWAY_URL = user_url

print(f"\n🚀 Отправляю запрос на: {RAILWAY_URL}/api/admin/reset-bp-tasks")

try:
    response = requests.post(
        f"{RAILWAY_URL}/api/admin/reset-bp-tasks",
        headers={
            "X-Admin-Key": ADMIN_KEY,
            "Content-Type": "application/json"
        },
        timeout=10
    )
    
    print(f"📊 Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ УСПЕШНО!")
        print(f"   🗑️  Удалено старых заданий: {data.get('deleted', '?')}")
        print(f"   ➕ Добавлено новых заданий: {data.get('added', '?')}")
        print(f"\n💬 Сообщение: {data.get('message', 'OK')}")
        print("\n✅ BP задания обновлены! На боте теперь 59 новых заданий!")
        sys.exit(0)
    
    elif response.status_code == 403:
        print(f"\n❌ ОШИБКА: Неправильный админ-ключ!")
        print(f"   Используется ключ: {ADMIN_KEY}")
        print(f"   Ответ: {response.json()}")
        sys.exit(1)
    
    else:
        print(f"\n❌ ОШИБКА: {response.status_code}")
        print(f"   Ответ: {response.text}")
        sys.exit(1)

except requests.exceptions.ConnectionError:
    print(f"\n❌ ОШИБКА подключения!")
    print(f"   Не удалось подключиться к {RAILWAY_URL}")
    print(f"   Проверь:")
    print(f"   1. URL правильный?")
    print(f"   2. Приложение на Railway запущено?")
    print(f"   3. Интернет соединение работает?")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    sys.exit(1)
