import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient, events
from telethon.tl.types import UserStatusOnline, UserStatusOffline

# Импортируем конфигурацию
try:
    from config import API_ID, API_HASH, TARGET_USER_ID, NOTIFICATION_CHAT, SESSION_FILE
except ImportError:
    print("❌ Ошибка: Создайте файл config.py из config.py.example и заполните его!")
    sys.exit(1)

# Флаг для отслеживания текущего статуса
user_online_status = {}

client = TelegramClient('session', API_ID, API_HASH)

@client.on(events.UserUpdate())
async def handler(event):
    if event.user_id == TARGET_USER_ID:
        try:
            user = await event.get_user()
            
            if not hasattr(user, 'status'):
                return
            
            user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            current_time = datetime.now().strftime('%H:%M:%S')
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Проверяем статус "онлайн"
            if isinstance(user.status, UserStatusOnline):
                if user_online_status.get(event.user_id) != 'online':
                    user_online_status[event.user_id] = 'online'
                    
                    # Форматируем время окончания онлайна
                    expires = user.status.expires
                    if isinstance(expires, datetime):
                        expires_str = expires.strftime('%H:%M:%S')
                    elif isinstance(expires, (int, float)):
                        expires_str = datetime.fromtimestamp(expires).strftime('%H:%M:%S')
                    else:
                        expires_str = "неизвестно"
                    
                    message = f"""
🚨 {user_name} СЕЙЧАС ОНЛАЙН!

⏱️ Время обнаружения: {current_time}
📅 Дата: {current_date}
⏳ Онлайн до: {expires_str}

ID: {TARGET_USER_ID}
                    """
                    
                    await client.send_message(NOTIFICATION_CHAT, message)
                    print(f"[{current_time}] ✅ {user_name} онлайн. Уведомление отправлено.")
            
            # Проверяем статус "оффлайн"
            elif isinstance(user.status, UserStatusOffline):
                if user_online_status.get(event.user_id) != 'offline':
                    user_online_status[event.user_id] = 'offline'
                    
                    # Получаем время последнего онлайна
                    was_online = user.status.was_online
                    was_online_str = was_online.strftime('%H:%M:%S')
                    was_online_date = was_online.strftime('%Y-%m-%d')
                    
                    # ИСПРАВЛЕНИЕ: Безопасное вычисление разницы во времени
                    try:
                        # Приводим оба времени к UTC для сравнения
                        now_utc = datetime.now(timezone.utc)
                        
                        # Если was_online уже имеет временную зону
                        if was_online.tzinfo is not None:
                            was_online_utc = was_online.astimezone(timezone.utc)
                        else:
                            # Предполагаем, что was_online в UTC
                            was_online_utc = was_online.replace(tzinfo=timezone.utc)
                        
                        # Вычисляем разницу
                        time_diff = now_utc - was_online_utc
                        minutes_ago = int(time_diff.total_seconds() / 60)
                        
                    except Exception as time_error:
                        print(f"⚠️ Ошибка вычисления времени: {time_error}")
                        minutes_ago = 0  # Значение по умолчанию
                    
                    message = f"""
🔴 {user_name} ВЫШЕЛ(А) ИЗ СЕТИ

⏱️ Время обнаружения: {current_time}
📅 Дата: {current_date}
🕐 Был(а) онлайн в: {was_online_str}
📅 Был(а) онлайн: {was_online_date}
⏰ Прошло с онлайна: {minutes_ago} минут

ID: {TARGET_USER_ID}
                    """
                    
                    await client.send_message(NOTIFICATION_CHAT, message)
                    print(f"[{current_time}] 🔴 {user_name} оффлайн. Уведомление отправлено.")
            
            else:
                status_name = type(user.status).__name__
                print(f"[{current_time}] ⚪ {user_name}: {status_name}")
                
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")

async def main():
    await client.start()
    print("=" * 50)
    print("🤖 Трекер онлайн/оффлайн статуса Telegram")
    print(f"📱 Отслеживаю пользователя с ID: {TARGET_USER_ID}")
    print(f"📨 Уведомления отправляются в: {NOTIFICATION_CHAT}")
    print("=" * 50)
    
    print("✅ Авторизован как:", (await client.get_me()).first_name)
    
    try:
        user = await client.get_entity(TARGET_USER_ID)
        user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        print(f"👤 Отслеживаю пользователя: {user_name}")
        
        if hasattr(user, 'status'):
            if isinstance(user.status, UserStatusOnline):
                user_online_status[TARGET_USER_ID] = 'online'
                print(f"📊 Начальный статус: 🟢 Онлайн")
            elif isinstance(user.status, UserStatusOffline):
                user_online_status[TARGET_USER_ID] = 'offline'
                print(f"📊 Начальный статус: 🔴 Не в сети")
            else:
                user_online_status[TARGET_USER_ID] = 'unknown'
                print(f"📊 Начальный статус: ⚪ Другой")
    except Exception as e:
        print(f"❌ Ошибка получения пользователя: {e}")
        return
    
    await client.send_message(NOTIFICATION_CHAT, 
        f"🎯 Начинаю отслеживание статуса {user_name}\n"
        f"Буду уведомлять о входе в онлайн и выходе из сети.\n"
        f"ID: {TARGET_USER_ID}"
    )
    print("📤 Стартовое уведомление отправлено")
    
    print("\n🤖 Бот запущен. Ожидаю изменения статуса...")
    print("Нажмите Ctrl+C для остановки")
    print("=" * 50)
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
