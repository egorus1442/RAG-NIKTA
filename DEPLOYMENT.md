# 🚀 Развертывание RAG API на сервере

## 📋 Требования к серверу

- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Минимум 2GB (рекомендуется 4GB+)
- **CPU**: 2 ядра (рекомендуется 4+)
- **Диск**: 10GB+ свободного места
- **Сеть**: Статический IP или домен

## 🐳 Способ 1: Docker (Рекомендуется)

### Быстрое развертывание

```bash
# 1. Клонируйте репозиторий
git clone <your-repo-url>
cd RAG

# 2. Настройте переменные окружения
cp example.env .env
nano .env  # Отредактируйте API ключи

# 3. Запустите развертывание
./deploy.sh
```

### Ручное развертывание

```bash
# 1. Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. Установите Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Создайте .env файл
cp example.env .env
# Отредактируйте .env с вашими ключами

# 4. Запустите приложение
docker-compose up -d

# 5. Проверьте статус
docker-compose ps
curl http://localhost:8000/health
```

## 🐧 Способ 2: Systemd Service

### Установка зависимостей

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python и зависимости
sudo apt install -y python3 python3-pip python3-venv poppler-utils

# Создайте пользователя
sudo useradd -r -s /bin/false rag-user
sudo mkdir -p /opt/rag
sudo chown rag-user:rag-user /opt/rag
```

### Настройка приложения

```bash
# Скопируйте код
sudo cp -r . /opt/rag/
sudo chown -R rag-user:rag-user /opt/rag

# Создайте виртуальное окружение
cd /opt/rag
sudo -u rag-user python3 -m venv venv
sudo -u rag-user venv/bin/pip install -r requirements.txt

# Настройте переменные окружения
sudo -u rag-user cp example.env .env
sudo nano .env  # Отредактируйте ключи
```

### Настройка systemd

```bash
# Скопируйте service файл
sudo cp rag-api.service /etc/systemd/system/

# Отредактируйте переменные окружения в service файле
sudo nano /etc/systemd/system/rag-api.service

# Включите и запустите сервис
sudo systemctl daemon-reload
sudo systemctl enable rag-api
sudo systemctl start rag-api

# Проверьте статус
sudo systemctl status rag-api
```

## 🌐 Настройка веб-сервера (Nginx)

### Установка Nginx

```bash
sudo apt install -y nginx
```

### Настройка конфигурации

```bash
# Скопируйте конфигурацию
sudo cp nginx.conf /etc/nginx/sites-available/rag-api

# Отредактируйте домен
sudo nano /etc/nginx/sites-available/rag-api

# Включите сайт
sudo ln -s /etc/nginx/sites-available/rag-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Настройка SSL (Let's Encrypt)

```bash
# Установите certbot
sudo apt install -y certbot python3-certbot-nginx

# Получите сертификат
sudo ./ssl-setup.sh
```

## 📊 Мониторинг

### Автоматический мониторинг

```bash
# Добавьте в crontab для проверки каждые 5 минут
crontab -e
# Добавьте строку:
*/5 * * * * /path/to/your/rag/monitoring.sh
```

### Просмотр логов

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u rag-api -f

# Nginx
sudo tail -f /var/log/nginx/rag_api_access.log
sudo tail -f /var/log/nginx/rag_api_error.log
```

## 🔧 Управление

### Docker команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление
git pull
docker-compose build
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### Systemd команды

```bash
# Запуск
sudo systemctl start rag-api

# Остановка
sudo systemctl stop rag-api

# Перезапуск
sudo systemctl restart rag-api

# Статус
sudo systemctl status rag-api

# Просмотр логов
sudo journalctl -u rag-api -f
```

## 🔒 Безопасность

### Firewall

```bash
# Откройте только нужные порты
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Обновления

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# В docker-compose.yml добавьте:
services:
  rag-api:
    deploy:
      replicas: 3
    environment:
      - WORKERS=4
```

### Вертикальное масштабирование

```bash
# Увеличьте ресурсы в docker-compose.yml:
services:
  rag-api:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

## 🆘 Устранение неполадок

### Проверка статуса

```bash
# API здоровье
curl http://localhost:8000/health

# Docker статус
docker-compose ps

# Systemd статус
sudo systemctl status rag-api

# Логи
docker-compose logs
sudo journalctl -u rag-api
```

### Частые проблемы

1. **API недоступен**: Проверьте порты и firewall
2. **Ошибки API ключей**: Проверьте .env файл
3. **Нехватка памяти**: Увеличьте swap или RAM
4. **Медленная работа**: Проверьте диск и сеть

## 📞 Поддержка

- **Логи**: `docker-compose logs` или `sudo journalctl -u rag-api`
- **Мониторинг**: `./monitoring.sh`
- **Документация**: http://your-domain.com/docs 