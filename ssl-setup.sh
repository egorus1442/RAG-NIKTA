set -e

echo "🔒 Настройка SSL сертификата..."

# Проверяем наличие certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 Устанавливаем certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Запрашиваем домен
read -p "Введите ваш домен (например: rag.yourdomain.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ Домен не указан"
    exit 1
fi

# Обновляем nginx конфигурацию
echo "📝 Обновляем nginx конфигурацию..."
sudo cp nginx.conf /etc/nginx/sites-available/rag-api
sudo sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/rag-api
sudo ln -sf /etc/nginx/sites-available/rag-api /etc/nginx/sites-enabled/

# Проверяем конфигурацию nginx
sudo nginx -t

# Получаем SSL сертификат
echo "🔐 Получаем SSL сертификат..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Настраиваем автообновление
echo "🔄 Настраиваем автообновление сертификата..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL сертификат настроен!"
echo "🌐 Ваш API доступен по адресу: https://$DOMAIN" 