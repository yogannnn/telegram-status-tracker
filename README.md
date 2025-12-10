# Telegram Status Tracker Bot

Бот для отслеживания онлайн-статуса пользователя Telegram и отправки уведомлений о его появлении в сети.

##  Возможности
*   Мгновенное оповещение о входе пользователя в онлайн.
*   Оповещение о выходе пользователя из сети.
*   Работа в фоне как система systemd служба (автозапуск, перезапуск при сбоях).

##  Установка и настройка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/ВАШ_ЛОГИН/telegram-status-tracker.git
    cd telegram-status-tracker
    ```

2.  **Установите зависимости:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Настройте конфигурацию:**
    ```bash
    cp config.py.example config.py
    nano config.py  # Отредактируйте файл, вставив свои API_ID, API_HASH и ID целевого пользователя
    ```

4.  **Запустите бота в первый раз для авторизации:**
    ```bash
    python telegram-status-tracker.py
    ```
    Следуйте инструкциям в терминале (введите номер телефона, код подтверждения).

5.  **(Опционально) Настройте автоматический запуск через systemd:**
    ```bash
    # Отредактируйте пример файла службы
    cp systemd/tg_status_tracker.service.example systemd/tg_status_tracker.service
    nano systemd/tg_status_tracker.service
    # Укажите верные пути (WorkingDirectory, ExecStart) и имя пользователя (User)
    sudo cp systemd/tg_status_tracker.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now tg_status_tracker.service
    ```

##  Использование
После настройки бот будет работать автоматически. Проверьте статус службы:
```bash
sudo systemctl status tg_status_tracker.service
```
Просмотр логов в реальном времени:
```bash
sudo journalctl -u tg_status_tracker.service -f
```

##  Важная информация
*   **Никогда не публикуйте** свой файл `config.py` или `*.session`!
*   Бот требует, чтобы отслеживаемый пользователь был у вас в контактах.
*   Убедитесь, что настройки приватности пользователя позволяют видеть его онлайн-статус.
