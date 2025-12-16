# 🌐 Развертывание на продакшн

Руководство по развертыванию Telegram бота с Web App на различные платформы.

## 📋 Предварительные требования

- [ ] Токен бота от @BotFather
- [ ] Аккаунт на облачной платформе
- [ ] Установленный Git
- [ ] Установленный Python 3.9+

## 🎯 Выбор платформы

### 🟢 Вариант 1: Heroku (Самый легкий)

**Плюсы:**
- ✅ Легко развертывать
- ✅ Бесплатный план раньше был (сейчас платный)
- ✅ Автоматические обновления

**Минусы:**
- ❌ Платный
- ❌ Засыпает на бесплатном плане

#### Шаги:

1. **Создайте аккаунт:**
   - Откройте https://www.heroku.com
   - Зарегистрируйтесь

2. **Установите Heroku CLI:**
   ```bash
   # Windows
   # Скачайте с https://devcenter.heroku.com/articles/heroku-cli
   
   # Linux/Mac
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

3. **Логин:**
   ```bash
   heroku login
   ```

4. **Создайте приложение:**
   ```bash
   heroku create your-app-name
   ```

5. **Создайте Procfile:**
   ```bash
   echo "web: python -m bot.main" > Procfile
   ```

6. **Установите токен:**
   ```bash
   heroku config:set BOT_TOKEN=your_token_here
   ```

7. **Разверните:**
   ```bash
   git push heroku main
   ```

---

### 🟦 Вариант 2: DigitalOcean (Рекомендуется)

**Плюсы:**
- ✅ Надежный сервис
- ✅ Полный контроль
- ✅ Доступные цены ($4-6/месяц)

**Минусы:**
- ❌ Нужно управлять сервером
- ❌ Настройка HTTPS

#### Шаги:

1. **Создайте Droplet:**
   - Откройте https://www.digitalocean.com
   - "Create" → "Droplet"
   - Выберите Ubuntu 22.04 LTS
   - Выберите $4-6/месяц
   - SSH ключ (рекомендуется)
   - "Create Droplet"

2. **SSH подключение:**
   ```bash
   ssh root@your_droplet_ip
   ```

3. **Обновите систему:**
   ```bash
   apt update && apt upgrade -y
   ```

4. **Установите зависимости:**
   ```bash
   apt install -y python3-pip python3-venv git
   ```

5. **Клонируйте репо:**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

6. **Создайте виртуальное окружение:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

7. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

8. **Создайте .env:**
   ```bash
   nano .env
   # BOT_TOKEN=your_token_here
   ```

9. **Запустите с gunicorn:**
   ```bash
   pip install gunicorn
   gunicorn -b 0.0.0.0:8000 bot.web.app:app &
   ```

10. **Настройте HTTPS (Let's Encrypt):**
    ```bash
    apt install -y certbot python3-certbot-nginx nginx
    certbot certonly --standalone -d your-domain.com
    ```

---

### 🐳 Вариант 3: Docker + Any Cloud

**Плюсы:**
- ✅ Портабельность
- ✅ Легко масштабировать
- ✅ Работает везде

**Минусы:**
- ❌ Сложнее настраивать

#### Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BOT_TOKEN=${BOT_TOKEN}

CMD ["python", "-m", "bot.main"]
```

#### docker-compose.yml:

```yaml
version: '3.9'

services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./bot_data.db:/app/bot_data.db
    restart: always
```

#### Запуск:

```bash
docker-compose up -d
```

---

### ☁️ Вариант 4: AWS (Scalable)

**Плюсы:**
- ✅ Масштабируемость
- ✅ Много опций
- ✅ Надежность

**Минусы:**
- ❌ Сложная настройка
- ❌ Может быть дороговато

#### Шаги (упрощенно):

1. Создайте EC2 инстанс (Ubuntu 22.04)
2. Выполните шаги как для DigitalOcean
3. Используйте AWS RDS для БД (опционально)
4. Используйте AWS S3 для бэкапов

---

## 🔐 Конфигурация для Production

### 1. Обновите URL Web App

Отредактируйте `bot/keyboards/keyboards.py`:

```python
# Локально
# WebAppInfo(url="http://localhost:5000")

# Production
WebAppInfo(url="https://your-domain.com")
```

### 2. Создайте .env на сервере

```bash
BOT_TOKEN=your_bot_token
WEB_APP_URL=https://your-domain.com
```

### 3. Настройте HTTPS

```bash
# Для DigitalOcean с Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

Обновите Flask для HTTPS:

```python
# bot/web/app.py
if __name__ == '__main__':
    ssl_context = ('path/to/cert.pem', 'path/to/key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=ssl_context)
```

### 4. Используйте Nginx как обратный прокси

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Мониторинг

### Логирование

```python
# bot/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

### Проверка статуса

```bash
# Heroku
heroku logs --tail

# DigitalOcean
journalctl -u bot -f

# Docker
docker logs -f container_name
```

## 💾 Резервные копии

### Автоматические бэкапы

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y-%m-%d_%H-%M-%S)
cp bot_data.db backup/bot_data_$DATE.db
```

### Облачные бэкапы (AWS S3)

```bash
pip install boto3
```

```python
import boto3

s3 = boto3.client('s3')
s3.upload_file('bot_data.db', 'my-bucket', 'bot_data.db')
```

## 🔄 Обновления

### Для Heroku:

```bash
git push heroku main
```

### Для DigitalOcean:

```bash
cd /path/to/bot
git pull origin main
pip install -r requirements.txt --upgrade
systemctl restart bot
```

### Для Docker:

```bash
docker-compose pull
docker-compose up -d
```

## ⚠️ Частые проблемы

### Проблема: Web App медленно загружается

**Решение:**
- Используйте CDN
- Оптимизируйте CSS/JS
- Включите кэширование

### Проблема: Бот не отвечает

**Решение:**
```bash
# Проверьте логи
tail -f bot.log

# Перезапустите
systemctl restart bot
```

### Проблема: БД растет слишком большой

**Решение:**
```python
# Добавьте удаление старых данных
from datetime import datetime, timedelta

old_date = datetime.now() - timedelta(days=90)
session.query(Sale).filter(Sale.created_at < old_date).delete()
```

## 🎯 Чеклист развертывания

- [ ] Получен токен от BotFather
- [ ] Выбрана платформа развертывания
- [ ] Создан аккаунт на платформе
- [ ] Проект загружен на GitHub (приватный)
- [ ] .env файл не в репозитории
- [ ] Web App URL обновлен
- [ ] HTTPS настроен
- [ ] Логирование настроено
- [ ] Бэкапы автоматизированы
- [ ] Мониторинг настроен
- [ ] DNS указывает на сервер
- [ ] Первый запуск протестирован
- [ ] Получены первые данные от юзеров
- [ ] All is working! 🎉

## 📚 Полезные ссылки

- [Heroku Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)
- [DigitalOcean Droplets](https://docs.digitalocean.com/products/droplets/getting-started/)
- [Docker Documentation](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Nginx Reverse Proxy](https://nginx.org/en/docs/)

---

**Версия:** 1.0  
**Последнее обновление:** Декабрь 2024
