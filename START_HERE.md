# START HERE: Исправление ошибки telegram_id

## Очень срочно? (30 секунд)

Выполните 3 команды:
```bash
git add .
git commit -m "Fix: Auto-migrate telegram_id to BigInteger"
git push origin main
```

Затем: Railway Dashboard → Services → bot → Redeploy

ГОТОВО! ✅

---

## Нужна информация? Читайте документы:

1. **QUICK_FIX.md** - самое краткое (30 сек)
2. **URGENT_FIX_README.md** - для Railway (2 мин)
3. **HOW_TO_FIX.md** - выбор сценария (2 мин)
4. **TELEGRAM_ID_FIX_SUMMARY.md** - полная справка (10 мин)

---

## Что произошло?

Telegram ID некоторых пользователей > 2.147 млрд, 
а Integer PostgreSQL может хранить только до ±2.1 млрд.

Решение: Integer → BigInteger (64-бит)

---

## Что будет после?

✅ Все пользователи смогут добавлять товары
✅ Ошибка исчезнет
✅ Никаких потерь данных

---

**Начните с git команд выше!**
