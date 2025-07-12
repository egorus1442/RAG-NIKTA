#!/bin/bash

# Скрипт развертывания RAG API на сервере
set -e

echo "🚀 Развертывание RAG API..."

# Проверяем наличие Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker найден"
else
    echo "❌ Docker не найден. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Перезагрузите систему и запустите скрипт снова."
    exit 1
fi

# Проверяем наличие docker-compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose найден"
else
    echo "❌ Docker Compose не найден. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен"
fi

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл..."
    cp example.env .env
    echo "⚠️  Отредактируйте .env файл с вашими API ключами!"
    echo "   - OPENAI_API_KEY"
    echo "   - OPENROUTER_API_KEY" 
    echo "   - API_TOKEN"
    read -p "Нажмите Enter после редактирования .env файла..."
fi

# Создаем директории
echo "📁 Создаем директории..."
mkdir -p uploads chroma_db
touch uploads/.gitkeep chroma_db/.gitkeep

# Собираем и запускаем контейнер
echo "🐳 Собираем Docker образ..."
docker-compose build

echo "🚀 Запускаем RAG API..."
docker-compose up -d

# Проверяем статус
echo "⏳ Ожидаем запуска сервиса..."
sleep 10

if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ RAG API успешно запущен!"
    echo "🌐 API доступен по адресу: http://localhost:8000"
    echo "📚 Документация: http://localhost:8000/docs"
    echo ""
    echo "📋 Полезные команды:"
    echo "   Просмотр логов: docker-compose logs -f"
    echo "   Остановка: docker-compose down"
    echo "   Перезапуск: docker-compose restart"
else
    echo "❌ Ошибка запуска. Проверьте логи:"
    docker-compose logs
    exit 1
fi 