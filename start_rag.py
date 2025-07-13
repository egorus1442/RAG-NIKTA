"""
Автоматический запуск RAG API с исправлением проблем
"""

import subprocess
import sys
import os

def run_command(command, description, check_output=False):
    """Выполняет команду"""
    print(f"🔧 {description}...")
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, ""
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False, ""

def check_and_fix_dependencies():
    """Проверяет и исправляет зависимости"""
    print("🔍 Проверка зависимостей...")
    
    # Проверяем NumPy
    success, output = run_command("python3 -c 'import numpy; print(numpy.__version__)'", "Проверка версии NumPy", True)
    if success and output.startswith('2.'):
        print(f"❌ Обнаружена несовместимая версия NumPy: {output}")
        print("🔧 Исправление NumPy...")
        run_command("python3 -m pip install 'numpy<2.0'", "Установка совместимой версии NumPy")
    
    # Проверяем six
    success, _ = run_command("python3 -c 'import six'", "Проверка six", True)
    if not success:
        print("🔧 Установка six...")
        run_command("python3 -m pip install 'six>=1.17.0'", "Установка six")
    
    # Проверяем dateutil
    success, _ = run_command("python3 -c 'import dateutil'", "Проверка dateutil", True)
    if not success:
        print("🔧 Установка python-dateutil...")
        run_command("python3 -m pip install --force-reinstall 'python-dateutil>=2.9.0'", "Установка python-dateutil")

def check_port():
    """Проверяет, занят ли порт 8000"""
    print("🔍 Проверка порта 8000...")
    success, output = run_command("lsof -i :8000", "Проверка порта", True)
    if success and output.strip():
        print("⚠️  Порт 8000 занят!")
        print("   Найденные процессы:")
        for line in output.strip().split('\n')[1:]:
            if line.strip():
                print(f"   {line.strip()}")
        return False
    print("✅ Порт 8000 свободен")
    return True

def main():
    """Основная функция"""
    print("🚀 Автоматический запуск RAG API")
    print("=" * 40)
    
    # Проверяем виртуальную среду
    if not os.environ.get('VIRTUAL_ENV'):
        print("❌ Виртуальная среда не активирована!")
        print("   Активируйте виртуальную среду: source venv/bin/activate")
        return False
    
    print(f"✅ Виртуальная среда: {os.environ.get('VIRTUAL_ENV')}")
    
    # Проверяем и исправляем зависимости
    check_and_fix_dependencies()
    
    # Проверяем порт
    if not check_port():
        print("\n❌ Порт 8000 занят. Освободите порт и попробуйте снова.")
        print("   Команды для освобождения порта:")
        print("   - lsof -i :8000  # найти процесс")
        print("   - kill -9 <PID>  # остановить процесс")
        return False
    
    # Проверяем .env файл
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("   Создайте файл .env на основе example.env")
        return False
    
    print("✅ Все проверки пройдены!")
    print("\n🚀 Запуск RAG API...")
    print("-" * 40)
    
    # Запускаем RAG API
    return run_command("python3 run.py", "Запуск RAG API")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 