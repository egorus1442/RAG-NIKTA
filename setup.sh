echo "🚀 Настройка RAG API проекта"
echo "=============================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"

# Создаем виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp example.env .env
    echo "⚠️  ВНИМАНИЕ: Отредактируйте файл .env и добавьте ваши API ключи!"
else
    echo "✅ Файл .env уже существует"
fi

echo ""
echo "🎉 Настройка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте файл .env и добавьте ваши API ключи"
echo "2. Активируйте виртуальное окружение: source venv/bin/activate"
echo "3. Запустите API: python run.py"
echo "4. Откройте документацию: http://localhost:8000/docs"
echo ""
echo "Для тестирования API используйте: python test_api.py" 