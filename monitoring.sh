# Скрипт мониторинга RAG API
set -e

API_URL="http://localhost:8000"
LOG_FILE="monitoring.log"

echo "📊 Мониторинг RAG API - $(date)" | tee -a $LOG_FILE

# Проверка здоровья API
echo "🔍 Проверка здоровья API..."
if curl -f -s $API_URL/health > /dev/null; then
    echo "✅ API работает" | tee -a $LOG_FILE
else
    echo "❌ API недоступен" | tee -a $LOG_FILE
    exit 1
fi

# Проверка использования диска
echo "💾 Проверка использования диска..."
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
echo "Использование диска: ${DISK_USAGE}%" | tee -a $LOG_FILE

if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️  Критическое использование диска!" | tee -a $LOG_FILE
fi

# Проверка размера логов
echo "📝 Проверка размера логов..."
if [ -f "rag_api.log" ]; then
    LOG_SIZE=$(du -h rag_api.log | cut -f1)
    echo "Размер лога: $LOG_SIZE" | tee -a $LOG_FILE
    
    # Ротация логов если больше 100MB
    if [ $(du -m rag_api.log | cut -f1) -gt 100 ]; then
        echo "🔄 Ротация логов..."
        mv rag_api.log rag_api.log.$(date +%Y%m%d_%H%M%S)
        touch rag_api.log
    fi
fi

# Проверка количества файлов
echo "📁 Статистика файлов..."
UPLOAD_COUNT=$(find uploads -name "*.txt" | wc -l)
echo "Обработанных файлов: $UPLOAD_COUNT" | tee -a $LOG_FILE

# Проверка Docker контейнеров (если используется Docker)
if command -v docker &> /dev/null; then
    echo "🐳 Проверка Docker контейнеров..."
    if docker ps | grep -q rag-api; then
        echo "✅ Контейнер RAG API запущен" | tee -a $LOG_FILE
    else
        echo "❌ Контейнер RAG API не запущен" | tee -a $LOG_FILE
    fi
fi

echo "✅ Мониторинг завершен" | tee -a $LOG_FILE
echo "---" | tee -a $LOG_FILE 