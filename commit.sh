#!/bin/bash
cd /d/bot
git add bot/web/static/app.js
git commit -m "Fix: Refresh inventory after sale, not main items list"
git push origin main
echo "✅ Успешно закоммичено и задеплоено"
