# flowerconfig.example.py
"""
Шаблон конфигурации Flower.
Скопируй в flowerconfig.py и замени на свои значения.
"""

import os

# Порт и адрес
port = int(os.environ.get('FLOWER_PORT', 5555))
address = '0.0.0.0'

# Базовая аутентификация
# ВАЖНО: Замени admin и flower123 на свои значения!
basic_auth = [
    f"{os.environ.get('FLOWER_USER', 'admin')}:{os.environ.get('FLOWER_PASSWORD', 'changeme')}"
]

# Префикс URL если за reverse proxy
# url_prefix = 'flower'

# Сохранять состояние между перезапусками
persistent = True
db = '/app/flower.db'

# Логирование
logging = 'info'

# Автообновление страницы
auto_refresh = True
natural_time = True
max_tasks = 10000