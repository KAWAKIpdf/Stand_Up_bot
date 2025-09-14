import telebot
import logging as std_logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import os
import time

std_logging.basicConfig(
    level=std_logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        std_logging.StreamHandler(),
        std_logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = std_logging.getLogger('Bot')

TOKEN = '7775082164:AAHovLa3Q-4906rtycSTbJ-_PgAkxwLVve8'

# Основные данные
comedians_list = "1. Жуков Дима\n"
censorship_rules = "❌ Избегай темы: религия, политика, дискриминация."
schedule_info = (
    "🗓️ Ближайшее выступление:\n"
    "📅 31 августа, 19:00\n\n"
    "🕒 Тайминг:\n"
    "• 18:30 - сбор гостей\n"
    "• 19:00 - начало шоу\n"
    "• 21:00 - финал"
)
socials_info = "📱 Наши соцсети:\n🔗 ВКонтакте: скоро будет\n📸 Instagram: скоро будет"
about_info = (
    "🎭 ФИЗТЕХ STAND UP\n\n"
    "🌟 КТО МЫ?\n"
    "Молодой стендап-клуб из лучшего технического ВУЗа России — МФТИ\n\n"

    "🚀 ЧТО МЫ ДЕЛАЕМ?\n"
    "• Проводим открытые микрофоны в общежитии\n"
    "• Организуем выступления на вузовских мероприятияв\n"
    "• Приглашаем профессиональных комиков (Константин Большаков, Дмитрий Ткачёв)\n"
    "• Участвуем в фестивалях VK и Панчлайн\n\n"

    "💫 ПОЧЕМУ МЫ?\n"
    "Создаём новое поколение tech-комиков и выводим студенческий юмор на новый уровень!"
)
places_info = "📍 Где мы выступаем:\n• ВК Фест\n• Клуб 6ки\n• Кампус МФТИ"
contacts_info = (
    "📞 Контакты для связи:\n"
    "📧 @kostyastrong - организатор\n"
    "💬 Напишите нам для сотрудничества!"
)
order_info = "☕️ Онлайн-заказ в 6ке\n\nСкоро будет доступна функции заказа напитков прямо через бота! Следите за обновлениями."
how_info = (
    "🎤 КАК СТАТЬ КОМИКОМ?\n\n"
    "1. 📝 Напиши нам в бота\n"
    "2. 🎭 Пройди короткую репетицию\n"
    "3. 🎫 Получи слот на выступление!\n\n"
    "Не бойся пробовать! У нас дружеская атмосфера 😊"
)
apply_info = (
    "📝 ЗАПОЛНИТЕ АНКЕТУ\n\n"
    "Для подачи заявки отправьте одним сообщением:\n\n"
    "1. 🎓 Ваш курс обучения\n"
    "2. 🏫 Физтех школа\n"
    "3. 🎤 Был ли опыт выступлений? (если да, то какой)\n\n"
    "📋 Пример:\n\"3 курс, ФПМИ, выступал в школе на концертах\""
)
wish_info = (
    "🌟 СОВЕТЫ НОВЫМ КОМИКАМ\n\n"
    "✨ Помни: тишина — это часть шоу. Будь собой и получай кайф!\n\n"
    "🎯 Почему стоит выступить с нами:\n"
    "• 🚀 Раскрой свой творческий потенциал\n"
    "• 💪 Получи бесценный опыт выступлений\n"
    "• 🤝 Стань частью нашего комьюнити\n\n"
    "Мы верим в тебя! Ты сможешь! 💫"
)

bot = telebot.TeleBot(TOKEN)

# Переменная для отслеживания аварийных перезапусков
emergency_restart = False


def is_admin(user_id):
    return db.user_has_role(user_id, 'admin')


def is_comedian(user_id):
    return db.user_has_role(user_id, 'comedian')


def can_send_photos(user_id):
    return is_admin(user_id) or is_comedian(user_id)


def create_main_menu_markup(user_id=None):
    markup = InlineKeyboardMarkup(row_width=2)

    # Основные кнопки
    buttons = [
        InlineKeyboardButton("👀 Я зритель", callback_data="viewer"),
        InlineKeyboardButton("🎤 Я комик", callback_data="new_comedian"),
        InlineKeyboardButton("💼 Спонсорам", callback_data="sponsor"),
        InlineKeyboardButton("🗓 Расписание", callback_data="schedule"),
        InlineKeyboardButton("📞 Контакты", callback_data="contacts"),
        InlineKeyboardButton("☕️ Заказ в 6ке", callback_data="order")
    ]

    # Специальные кнопки для админов и комиков
    if user_id and is_admin(user_id):
        buttons.append(InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin"))

    if user_id and can_send_photos(user_id):
        buttons.append(InlineKeyboardButton("📸 Отправить фото", callback_data="send_photo"))

    # Распределяем кнопки по рядам
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i + 1])
        else:
            markup.add(buttons[i])

    return markup


def create_start_button():
    """Создает кнопку для запуска бота"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Начать работу", callback_data="force_start"))
    return markup


def create_viewer_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👥 Список комиков", callback_data="comedians"),
        InlineKeyboardButton("📱 Соцсети", callback_data="socials"),
        InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
    )
    return markup


def create_comedian_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📜 Правила выступлений", callback_data="rules"),
        InlineKeyboardButton("❓ Как стать комиком", callback_data="how"),
        InlineKeyboardButton("💫 Советы новичкам", callback_data="wish"),
        InlineKeyboardButton("📝 Подать заявку", callback_data="apply"),
        InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
    )
    return markup


def create_sponsor_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎭 О нашем клубе", callback_data="about"),
        InlineKeyboardButton("📍 Места выступлений", callback_data="places"),
        InlineKeyboardButton("📞 Контакты", callback_data="contacts"),
        InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
    )
    return markup


def create_admin_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✏️ Список комиков", callback_data="edit_comedians"),
        InlineKeyboardButton("⚖️ Правила цензуры", callback_data="edit_rules"),
        InlineKeyboardButton("📅 Расписание", callback_data="edit_schedule"),
        InlineKeyboardButton("👑 Добавить админа", callback_data="add_admin"),
        InlineKeyboardButton("🎭 Добавить комика", callback_data="add_comedian"),
        InlineKeyboardButton("📸 Отправить фото", callback_data="send_photo"),
        InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
    )
    return markup


def send_restart_notification():
    """Отправляет уведомление о перезапуске всем пользователям только при аварийных ситуациях"""
    global emergency_restart

    if emergency_restart:
        logger.info("Отправка уведомления о аварийном перезапуске всем пользователям...")

        message_text = (
            "⚠️ Бот был перезапущен из-за технических неполадок!\n\n"
            "Для корректной работы бота нажмите кнопку ниже:\n"
        )

        all_users = db.get_all_users()
        success_count = 0
        fail_count = 0

        for user_id in all_users:
            try:
                markup = create_start_button()
                bot.send_message(user_id, message_text, reply_markup=markup)
                success_count += 1
            except Exception as e:
                fail_count += 1
                if "bot was blocked by the user" in str(e):
                    logger.warning(f"Пользователь {user_id} заблокировал бота")
                else:
                    logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")

        logger.info(f"Уведомления отправлены: Успешно - {success_count}, Ошибок - {fail_count}")

        # Сбрасываем флаг после отправки уведомлений
        emergency_restart = False


@bot.message_handler(commands=['start', 'menu', 'help'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    logger.info(f"Команда от пользователя: ID={user_id}, username={username}")

    # Автоматически добавляем пользователя в базу и даем роль viewer
    db.add_user(user_id, username, first_name, "")
    db.add_role_to_user(user_id, 'viewer')

    welcome_text = (
        "🎭 Добро пожаловать в Физтех Stand Up клуб!\n\n"
        "Мы проводим самые веселые стендап-вечера в МФТИ 🎤\n\n"
        "👇 Выберите, кто вы:"
    )

    send_main_menu(message.chat.id, welcome_text, user_id)


def send_main_menu(chat_id, text, user_id=None):
    markup = create_main_menu_markup(user_id)
    bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call.data == "force_start":
        welcome_text = (
            "🎭 Добро пожаловать в Физтех Stand Up клуб!\n\n"
            "Мы проводим самые веселые стендап-вечера в МФТИ 🎤\n\n"
            "👇 Выберите, кто вы:"
        )
        send_main_menu(chat_id, welcome_text, user_id)
        return

    if call.data == "main_menu":
        send_main_menu(chat_id, "🏠 Главное меню:", user_id)
        return

    if call.data == "viewer":
        markup = create_viewer_menu()
        bot.edit_message_text("👀 Меню для зрителей:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "new_comedian":
        markup = create_comedian_menu()
        bot.edit_message_text("🎤 Меню для комиков:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "sponsor":
        markup = create_sponsor_menu()
        bot.edit_message_text("💼 Меню для спонсоров:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "order":
        bot.send_message(chat_id, order_info)

    elif call.data == "contacts":
        bot.send_message(chat_id, contacts_info)

    elif call.data == "schedule":
        bot.send_message(chat_id, schedule_info)

    # Зрительские кнопки
    elif call.data == "comedians":
        bot.send_message(chat_id, f"🎤 Наши комики:\n\n{comedians_list}")
    elif call.data == "socials":
        bot.send_message(chat_id, socials_info)

    # Комические кнопки
    elif call.data == "rules":
        bot.send_message(chat_id, f"📜 Правила выступлений:\n\n{censorship_rules}")
    elif call.data == "how":
        bot.send_message(chat_id, how_info)
    elif call.data == "wish":
        bot.send_message(chat_id, wish_info)
    elif call.data == "apply":
        msg = bot.send_message(chat_id, apply_info)
        bot.register_next_step_handler(msg, process_application)

    # Спонсорские кнопки
    elif call.data == "about":
        bot.send_message(chat_id, about_info)
    elif call.data == "places":
        bot.send_message(chat_id, places_info)

    # Админские кнопки
    elif call.data == "admin" and is_admin(user_id):
        markup = create_admin_menu()
        bot.edit_message_text("⚙️ Админ-панель:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "edit_comedians" and is_admin(user_id):
        msg = bot.send_message(chat_id, "✏️ Введите новый список комиков (каждый с новой строки):")
        bot.register_next_step_handler(msg, save_comedians)
    elif call.data == "edit_rules" and is_admin(user_id):
        msg = bot.send_message(chat_id, "✏️ Введите новые правила цензуры:")
        bot.register_next_step_handler(msg, save_rules)
    elif call.data == "edit_schedule" and is_admin(user_id):
        msg = bot.send_message(chat_id, "✏️ Введите новое расписание:")
        bot.register_next_step_handler(msg, save_schedule)
    elif call.data == "add_admin" and is_admin(user_id):
        msg = bot.send_message(chat_id,
                               "👑 Для добавления администратора:\n\n"
                               "• Перешлите сообщение от пользователя\n"
                               "• Или отправьте его ID\n\n"
                               "Выберите любой из способов:"
                               )
        bot.register_next_step_handler(msg, save_admin)
    elif call.data == "add_comedian" and is_admin(user_id):
        msg = bot.send_message(chat_id,
                               "🎭 Для добавления комика:\n\n"
                               "• Перешлите сообщение от пользователя\n"
                               "• Или отправьте его ID\n\n"
                               "Выберите любой из способов:"
                               )
        bot.register_next_step_handler(msg, save_comedian)

    elif call.data == "send_photo" and can_send_photos(user_id):
        msg = bot.send_message(chat_id, "📸 Отправьте фото с подписью для рассылки всем пользователям:")
        bot.register_next_step_handler(msg, process_photo_submission)


def process_application(message):
    user_id = message.from_user.id
    username = message.from_user.username
    application_text = message.text

    logger.info(f"Получена анкета от пользователя: ID={user_id}, username={username}")

    admin_ids = db.get_users_with_role('admin')

    if not admin_ids:
        bot.send_message(message.chat.id, "❌ В настоящее время нет администраторов для обработки заявки.")
        return

    application_message = (
        f"📝 НОВАЯ ЗАЯВКА ОТ КОМИКА\n\n"
        f"👤 Пользователь: @{username if username else 'без username'}\n"
        f"📋 Анкета:\n{application_text}"
    )

    success_count = 0
    for admin_id in admin_ids:
        try:
            bot.send_message(admin_id, application_message)
            success_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить заявку администратору {admin_id}: {e}")

    if success_count > 0:
        bot.send_message(message.chat.id,
                         "✅ Ваша заявка отправлена администраторам! Ожидайте ответа в течение 24 часов.")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить заявку. Попробуйте позже.")


def process_photo_submission(message):
    user_id = message.from_user.id

    if not can_send_photos(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав для отправки фото.")
        return

    if not message.photo:
        bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте фото.")
        return

    photo = message.photo[-1]
    caption = message.caption or ""

    bot.send_message(message.chat.id, "✅ Фото получено. Начинаю рассылку...")

    success_count = 0
    fail_count = 0
    all_users = db.get_all_users()

    for target_user_id in all_users:
        try:
            if target_user_id != user_id:
                sender_info = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name}"
                full_caption = f"📸 Новое фото от {sender_info}:\n\n{caption}" if caption else f"📸 Новое фото от {sender_info}"

                bot.send_photo(target_user_id, photo.file_id, caption=full_caption)
                success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"Ошибка отправки фото пользователю {target_user_id}: {e}")

    bot.send_message(message.chat.id, f"✅ Рассылка завершена!\n\n✔️ Успешно: {success_count}\n❌ Ошибок: {fail_count}")


def save_comedians(message):
    global comedians_list
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 Нет прав.")
        return

    if not message.text:
        bot.send_message(message.chat.id, "❌ Список не может быть пустым.")
        return

    comedians_list = message.text
    bot.send_message(message.chat.id, "✅ Список комиков обновлён.")


def save_rules(message):
    global censorship_rules
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 Нет прав.")
        return

    if not message.text:
        bot.send_message(message.chat.id, "❌ Правила не могут быть пустыми.")
        return

    censorship_rules = message.text
    bot.send_message(message.chat.id, "✅ Правила обновлены.")


def save_schedule(message):
    global schedule_info
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 Нет прав.")
        return

    if not message.text:
        bot.send_message(message.chat.id, "❌ Расписание не может быть пустым.")
        return

    schedule_info = message.text
    bot.send_message(message.chat.id, "✅ Расписание обновлено.")


def save_admin(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 Нет прав.")
        return

    try:
        if message.forward_from:
            # Добавление по пересланному сообщению
            new_admin_id = message.forward_from.id
            username = message.forward_from.username or "пользователь"
            first_name = message.forward_from.first_name or ""
            last_name = message.forward_from.last_name or ""

            # Просто добавляем пользователя и даем права админа
            db.add_user(new_admin_id, username, first_name, last_name)
            db.add_role_to_user(new_admin_id, 'admin')

            bot.send_message(message.chat.id, f"✅ Пользователь @{username} назначен админом!")

            # Пытаемся отправить уведомление
            try:
                congratulation = "🎉 Вы назначены администратором! Теперь можете отправлять фото через бота."
                bot.send_message(new_admin_id, congratulation)
            except:
                logger.info(f"Не удалось отправить уведомление пользователю {new_admin_id}")

        else:
            # Добавление по ID
            new_admin_id = int(message.text.strip())

            # Просто добавляем пользователя и даем права админа
            db.add_user(new_admin_id)
            db.add_role_to_user(new_admin_id, 'admin')

            bot.send_message(message.chat.id, f"✅ Пользователь {new_admin_id} назначен админом!")

            # Пытаемся отправить уведомление
            try:
                congratulation = "🎉 Вы назначены администратором! Теперь можете отправлять фото через бота."
                bot.send_message(new_admin_id, congratulation)
            except:
                logger.info(f"Не удалось отправить уведомление пользователю {new_admin_id}")

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ID. ID должен быть числом.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при добавлении администратора: {e}")


def save_comedian(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 Нет прав.")
        return

    try:
        if message.forward_from:
            # Добавление по пересланному сообщению
            new_comedian_id = message.forward_from.id
            username = message.forward_from.username or "пользователь"
            first_name = message.forward_from.first_name or ""
            last_name = message.forward_from.last_name or ""

            # Просто добавляем пользователя и даем права комика
            db.add_user(new_comedian_id, username, first_name, last_name)
            db.add_role_to_user(new_comedian_id, 'comedian')

            bot.send_message(message.chat.id, f"✅ Пользователь @{username} назначен комиком!")

            # Пытаемся отправить уведомление
            try:
                congratulation = "🎉 Вы назначены комиком! Теперь можете отправлять фото своих выступлений."
                bot.send_message(new_comedian_id, congratulation)
            except:
                logger.info(f"Не удалось отправить уведомление пользователю {new_comedian_id}")

        else:
            # Добавление по ID
            new_comedian_id = int(message.text.strip())

            # Просто добавляем пользователя и даем права комика
            db.add_user(new_comedian_id)
            db.add_role_to_user(new_comedian_id, 'comedian')

            bot.send_message(message.chat.id, f"✅ Пользователь {new_comedian_id} назначен комиком!")

            # Пытаемся отправить уведомление
            try:
                congratulation = "🎉 Вы назначены комиком! Теперь можете отправлять фото своих выступлений."
                bot.send_message(new_comedian_id, congratulation)
            except:
                logger.info(f"Не удалось отправить уведомление пользователю {new_comedian_id}")

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ID. ID должен быть числом.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при добавлении комика: {e}")


@bot.message_handler(func=lambda message: True)
def auto_register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    # Автоматически добавляем пользователя и даем роль viewer
    db.add_user(user_id, username, first_name, last_name)
    db.add_role_to_user(user_id, 'viewer')


def start_bot():
    """Функция для запуска бота"""
    global emergency_restart

    logger.info("=" * 50)
    logger.info("✅ БОТ ЗАПУЩЕН И РАБОТАЕТ")
    logger.info("=" * 50)

    stats = db.get_database_stats()
    logger.info(f"📊 Всего пользователей: {stats['total_users']}")

    # Отправляем уведомление только при аварийных перезапусках
    if emergency_restart:
        send_restart_notification()

    bot.infinity_polling(timeout=10, long_polling_timeout=5)


def run_bot_with_exponential_backoff(max_attempts=10, initial_delay=5, max_delay=300):
    """Запуск бота с экспоненциальной задержкой при ошибках"""
    global emergency_restart
    attempts = 0
    delay = initial_delay

    while attempts < max_attempts:
        try:
            logger.info(f"Запуск бота (попытка {attempts + 1})")
            start_bot()

        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
            break

        except Exception as e:
            attempts += 1
            logger.error(f"Ошибка: {e}")

            # Устанавливаем флаг аварийного перезапуска
            emergency_restart = True

            if attempts >= max_attempts:
                logger.error("Максимальное количество попыток достигнуто")
                break

            logger.info(f"Перезапуск через {delay} секунд...")
            time.sleep(delay)

            # Экспоненциальная задержка
            delay = min(delay * 2, max_delay)


if __name__ == "__main__":
    run_bot_with_exponential_backoff()
