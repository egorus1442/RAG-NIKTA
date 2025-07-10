#!/usr/bin/env python3
"""
Скрипт для исправления проблем с зависимостями RAG API
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
        else:
            print(f"❌ {description} - ошибка")
            if result.stderr.strip():
                print(f"   {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def check_port_usage():
    """Проверяет, занят ли порт 8000"""
    print("🔍 Проверка порта 8000...")
    try:
        result = subprocess.run("lsof -i :8000", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("⚠️  Порт 8000 занят!")
            print("   Найденные процессы:")
            for line in result.stdout.strip().split('\n')[1:]:  # Пропускаем заголовок
                if line.strip():
                    print(f"   {line.strip()}")
            return True
        else:
            print("✅ Порт 8000 свободен")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки порта: {e}")
        return True

def main():
    """Основная функция исправления"""
    print("🚀 Исправление проблем с зависимостями RAG API")
    print("=" * 50)
    
    # Проверяем, активирована ли виртуальная среда
    if not os.environ.get('VIRTUAL_ENV'):
        print("❌ Виртуальная среда не активирована!")
        print("   Активируйте виртуальную среду: source venv/bin/activate")
        return False
    
    print(f"✅ Виртуальная среда: {os.environ.get('VIRTUAL_ENV')}")
    
    # Проверяем порт
    port_occupied = check_port_usage()
    
    # Исправляем зависимости
    success = True
    
    # Обновляем pip
    success &= run_command("python3 -m pip install --upgrade pip", "Обновление pip")
    
    # Устанавливаем совместимую версию NumPy
    success &= run_command("python3 -m pip install 'numpy<2.0'", "Установка совместимой версии NumPy")
    
    # Устанавливаем six
    success &= run_command("python3 -m pip install 'six>=1.17.0'", "Установка six")
    
    # Переустанавливаем python-dateutil
    success &= run_command("python3 -m pip install --force-reinstall 'python-dateutil>=2.9.0'", "Переустановка python-dateutil")
    
    # Устанавливаем все зависимости из requirements.txt
    success &= run_command("python3 -m pip install -r requirements.txt", "Установка зависимостей из requirements.txt")
    
    print("\n" + "=" * 50)
    
    if success:
        print("✅ Все зависимости исправлены!")
        
        if port_occupied:
            print("\n⚠️  ВНИМАНИЕ: Порт 8000 занят!")
            print("   Для запуска RAG API освободите порт 8000 или измените порт в run.py")
            print("   Команды для освобождения порта:")
            print("   - lsof -i :8000  # найти процесс")
            print("   - kill -9 <PID>  # остановить процесс")
        else:
            print("✅ Порт 8000 свободен - можно запускать RAG API")
        
        print("\n🚀 Для запуска RAG API выполните:")
        print("   python3 run.py")
        
        return True
    else:
        print("❌ Некоторые проблемы не удалось исправить")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 