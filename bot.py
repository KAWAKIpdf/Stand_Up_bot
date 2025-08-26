import telebot
import logging as std_logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db

# Настройка логирования для бота
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

# Глобальные переменные для хранения текстовых данных
comedians_list = "1. Жуков Дима\n"
censorship_rules = "Избегайте тем: религия, политика, дискриминация."
schedule_info = (
    "📅 31 августа, 19:00\n"
    "🕒 Тайминг:\n"
    "18:30 сбор гостей\n"
    "19:00 начало\n"
    "21:00 финал"
)
socials_info = "🔗 ВКонтакте: https://vk.com/yourgroup"
about_info = "Мы — Физтех Stand_up клуб. Были на ВК Фесте."
places_info = "📍 ВК Фест\n📍 Клуб 6ки"
contacts_info = "📧 @kostyastrong"
order_info = "☕️ Онлайн-заказ в 6ки доступен всем — [меню здесь](https://menu-link.com)"
how_info = (
    "1. Напиши нам в бот\n"
    "2. Пройди короткую репетицию\n"
    "3. Получи слот на выступление!"
)
apply_info = (
    "📝 Для подачи заявки, пожалуйста, отправьте следующую информацию:\n"
    "1. Ваше имя и возраст\n"
    "2. Небольшое описание вашего стиля юмора\n"
    "3. Есть ли у вас опыт выступлений? (если да, то какой)\n\n"
    "Отправьте это сообщение одним текстом."
)
wish_info = "✨ Помни: тишина — это часть шоу. Будь собой и получай кайф!"

bot = telebot.TeleBot(TOKEN)


def is_admin(user_id):
    return db.user_has_role(user_id, 'admin')


def is_comedian(user_id):
    return db.user_has_role(user_id, 'comedian')


def can_send_photos(user_id):
    return db.user_has_role(user_id, 'photo_sender') or is_admin(user_id) or is_comedian(user_id)


def create_main_menu_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👀 Я зритель", callback_data="viewer"))
    markup.add(InlineKeyboardButton("🎤 Я новый комик", callback_data="new_comedian"))
    markup.add(InlineKeyboardButton("💼 Я спонсор", callback_data="sponsor"))
    markup.add(InlineKeyboardButton("☕️ Онлайн-заказ в 6ки", callback_data="order"))

    if is_admin(user_id):
        markup.add(InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin"))

    if can_send_photos(user_id):
        markup.add(InlineKeyboardButton("📸 Отправить фото", callback_data="send_photo"))

    return markup


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    logger.info(f"Команда /start от пользователя: ID={user_id}, username={username}, first_name={first_name}")

    # Добавляем пользователя в базу данных
    db.add_user(user_id, username, first_name, last_name)

    # Даем роль viewer по умолчанию
    if not db.user_has_role(user_id, 'viewer'):
        db.add_role_to_user(user_id, 'viewer')

    markup = create_main_menu_markup(user_id)
    bot.send_message(message.chat.id, "Привет! Кто ты?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    username = call.from_user.username

    logger.info(f"Callback от пользователя: ID={user_id}, username={username}, data={call.data}")

    if call.data == "viewer":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 Список комиков", callback_data="comedians"))
        markup.add(InlineKeyboardButton("🗓 Расписание", callback_data="schedule"))
        markup.add(InlineKeyboardButton("🔗 Наши соцсети", callback_data="socials"))
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id, "Меню для зрителей:", reply_markup=markup)

    elif call.data == "new_comedian":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📜 Правила и цензура", callback_data="rules"))
        markup.add(InlineKeyboardButton("📘 Как стать комиком", callback_data="how"))
        markup.add(InlineKeyboardButton("🌟 Напутствие", callback_data="wish"))
        markup.add(InlineKeyboardButton("📝 Заполнить анкету", callback_data="apply"))
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id, "Меню для комиков:", reply_markup=markup)

    elif call.data == "sponsor":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🚀 О нас", callback_data="about"))
        markup.add(InlineKeyboardButton("📸 Где выступали", callback_data="places"))
        markup.add(InlineKeyboardButton("📞 Контакты", callback_data="contacts"))
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id, "Меню для спонсоров:", reply_markup=markup)

    elif call.data == "comedians":
        bot.send_message(call.message.chat.id, comedians_list)
    elif call.data == "schedule":
        bot.send_message(call.message.chat.id, schedule_info)
    elif call.data == "socials":
        bot.send_message(call.message.chat.id, socials_info)

    elif call.data == "rules":
        bot.send_message(call.message.chat.id, censorship_rules)
    elif call.data == "how":
        bot.send_message(call.message.chat.id, how_info)
    elif call.data == "wish":
        bot.send_message(call.message.chat.id, wish_info)
    elif call.data == "apply":
        bot.send_message(call.message.chat.id, apply_info)

    elif call.data == "about":
        bot.send_message(call.message.chat.id, about_info)
    elif call.data == "places":
        bot.send_message(call.message.chat.id, places_info)
    elif call.data == "contacts":
        bot.send_message(call.message.chat.id, contacts_info)

    elif call.data == "order":
        bot.send_message(call.message.chat.id, order_info, parse_mode="Markdown", disable_web_page_preview=True)

    elif call.data == "admin" and is_admin(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📝 Редактировать комиков", callback_data="edit_comedians"))
        markup.add(InlineKeyboardButton("🛡 Редактировать правила", callback_data="edit_rules"))
        markup.add(InlineKeyboardButton("👑 Назначить администратора", callback_data="add_admin"))
        markup.add(InlineKeyboardButton("🎭 Назначить комика", callback_data="add_comedian"))
        markup.add(InlineKeyboardButton("📸 Назначить отправителя фото", callback_data="add_photo_sender"))
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id, "⚙️ Админ-панель:", reply_markup=markup)

    elif call.data == "edit_comedians" and is_admin(user_id):
        msg = bot.send_message(call.message.chat.id, "✏️ Отправьте новый список комиков:")
        bot.register_next_step_handler(msg, save_comedians)
    elif call.data == "edit_rules" and is_admin(user_id):
        msg = bot.send_message(call.message.chat.id, "✏️ Отправьте новые правила цензуры:")
        bot.register_next_step_handler(msg, save_rules)
    elif call.data == "add_admin" and is_admin(user_id):
        msg = bot.send_message(call.message.chat.id,
                               "Перешлите любое сообщение от нового администратора (или отправьте его ID):")
        bot.register_next_step_handler(msg, save_admin)
    elif call.data == "add_comedian" and is_admin(user_id):
        msg = bot.send_message(call.message.chat.id,
                               "Перешлите любое сообщение от нового комика (или отправьте его ID):")
        bot.register_next_step_handler(msg, save_comedian)
    elif call.data == "add_photo_sender" and is_admin(user_id):
        msg = bot.send_message(call.message.chat.id,
                               "Перешлите любое сообщение от пользователя, который может отправлять фото (или отправьте его ID):")
        bot.register_next_step_handler(msg, save_photo_sender)

    elif call.data == "send_photo" and can_send_photos(user_id):
        msg = bot.send_message(call.message.chat.id,
                               "📸 Отправьте фото с подписью, которое хотите разослать всем пользователям:")
        bot.register_next_step_handler(msg, process_photo_submission)

    elif call.data == "back_to_main":
        markup = create_main_menu_markup(user_id)
        bot.send_message(call.message.chat.id, "Привет! Кто ты?", reply_markup=markup)


def process_photo_submission(message):
    user_id = message.from_user.id
    username = message.from_user.username

    logger.info(f"Попытка отправки фото от пользователя: ID={user_id}, username={username}")

    if not can_send_photos(user_id):
        bot.send_message(message.chat.id, "🚫 У вас нет прав для отправки фото.")
        return

    if not message.photo:
        bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте фото.")
        return

    photo = message.photo[-1]
    caption = message.caption or ""

    bot.send_message(message.chat.id, "✅ Фото получено. Рассылаю всем зарегистрированным пользователям...")

    success_count = 0
    fail_count = 0
    all_users = db.get_all_users()

    logger.info(f"Начинается рассылка фото пользователям: {len(all_users)} получателей")

    for target_user_id in all_users:
        try:
            if target_user_id != user_id:
                sender_info = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name}"
                full_caption = f"📷 Новое фото от {sender_info}:\n\n{caption}" if caption else f"📷 Новое фото от {sender_info}"

                bot.send_photo(target_user_id, photo.file_id, caption=full_caption)
                success_count += 1
        except telebot.apihelper.ApiException as e:
            fail_count += 1
            if "bot was blocked by the user" in str(e):
                logger.warning(f"Пользователь {target_user_id} заблокировал бота.")
            else:
                logger.error(f"Не удалось отправить фото пользователю {target_user_id}: {e}")
        except Exception as e:
            fail_count += 1
            logger.error(f"Неизвестная ошибка при отправке фото пользователю {target_user_id}: {e}")

    logger.info(f"Рассылка завершена: успешно={success_count}, ошибок={fail_count}")
    bot.send_message(message.chat.id,
                     f"✅ Рассылка завершена!\nУспешно доставлено: {success_count}\nОшибок: {fail_count}")


def save_comedians(message):
    global comedians_list
    user_id = message.from_user.id

    logger.info(f"Попытка редактирования списка комиков от пользователя: ID={user_id}")

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 У вас нет прав для выполнения этой команды.")
        return

    comedians_list = message.text
    logger.info(f"Список комиков обновлен пользователем: ID={user_id}")
    bot.send_message(message.chat.id, "✅ Список комиков обновлён.")


def save_rules(message):
    global censorship_rules
    user_id = message.from_user.id

    logger.info(f"Попытка редактирования правил от пользователя: ID={user_id}")

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 У вас нет прав для выполнения этой команды.")
        return

    censorship_rules = message.text
    logger.info(f"Правила цензуры обновлены пользователем: ID={user_id}")
    bot.send_message(message.chat.id, "✅ Правила обновлены.")


def save_admin(message):
    user_id = message.from_user.id

    logger.info(f"Попытка добавления администратора от пользователя: ID={user_id}")

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 У вас нет прав для выполнения этой команды.")
        return

    try:
        if message.forward_from:
            new_admin_id = message.forward_from.id
            db.add_user(new_admin_id, message.forward_from.username,
                        message.forward_from.first_name, message.forward_from.last_name)
        else:
            new_admin_id = int(message.text.strip())
            # Добавляем пользователя с минимальной информацией
            db.add_user(new_admin_id)

        db.add_role_to_user(new_admin_id, 'admin')
        logger.info(f"Новый администратор назначен: ID={new_admin_id}, назначил: ID={user_id}")
        bot.send_message(message.chat.id, f"✅ Пользователь с ID {new_admin_id} назначен админом.")
        try:
            bot.send_message(new_admin_id, "🎉 Поздравляем! Вы были назначены администратором бота.")
        except:
            logger.warning(f"Не удалось отправить уведомление новому администратору: ID={new_admin_id}")
    except (ValueError, AttributeError):
        bot.send_message(message.chat.id, "❌ Ошибка. Перешлите сообщение от пользователя или введите его числовой ID.")
    except Exception as e:
        logger.error(f"Ошибка при назначении админа: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка при назначении админа: {e}")


def save_comedian(message):
    user_id = message.from_user.id

    logger.info(f"Попытка добавления комика от пользователя: ID={user_id}")

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 У вас нет прав для выполнения этой команды.")
        return

    try:
        if message.forward_from:
            new_comedian_id = message.forward_from.id
            db.add_user(new_comedian_id, message.forward_from.username,
                        message.forward_from.first_name, message.forward_from.last_name)
        else:
            new_comedian_id = int(message.text.strip())
            db.add_user(new_comedian_id)

        db.add_role_to_user(new_comedian_id, 'comedian')
        logger.info(f"Новый комик назначен: ID={new_comedian_id}, назначил: ID={user_id}")
        bot.send_message(message.chat.id, f"✅ Пользователь с ID {new_comedian_id} назначен комиком.")
        try:
            bot.send_message(new_comedian_id, "🎉 Поздравляем! Вы были назначены комиком.")
        except:
            logger.warning(f"Не удалось отправить уведомление новому комику: ID={new_comedian_id}")
    except (ValueError, AttributeError):
        bot.send_message(message.chat.id, "❌ Ошибка. Перешлите сообщение от пользователя или введите его числовой ID.")
    except Exception as e:
        logger.error(f"Ошибка при назначении комика: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка при назначении комика: {e}")


def save_photo_sender(message):
    user_id = message.from_user.id

    logger.info(f"Попытка добавления отправителя фото от пользователя: ID={user_id}")

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "🚫 У вас нет прав для выполнения этой команды.")
        return

    try:
        if message.forward_from:
            new_sender_id = message.forward_from.id
            db.add_user(new_sender_id, message.forward_from.username,
                        message.forward_from.first_name, message.forward_from.last_name)
        else:
            new_sender_id = int(message.text.strip())
            db.add_user(new_sender_id)

        db.add_role_to_user(new_sender_id, 'photo_sender')
        logger.info(f"Новый отправитель фото назначен: ID={new_sender_id}, назначил: ID={user_id}")
        bot.send_message(message.chat.id, f"✅ Пользователь с ID {new_sender_id} теперь может отправлять фото.")
        try:
            bot.send_message(new_sender_id, "🎉 Теперь вы можете отправлять фото через бота.")
        except:
            logger.warning(f"Не удалось отправить уведомление новому отправителю фото: ID={new_sender_id}")
    except (ValueError, AttributeError):
        bot.send_message(message.chat.id, "❌ Ошибка. Перешлите сообщение от пользователя или введите его числовой ID.")
    except Exception as e:
        logger.error(f"Ошибка при назначении отправителя фото: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка при назначении отправителя фото: {e}")


@bot.message_handler(func=lambda message: True)
def auto_register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    logger.info(f"Авторегистрация пользователя: ID={user_id}, username={username}")

    # Добавляем пользователя в базу, если его нет
    db.add_user(user_id, username, first_name, last_name)

    # Даем роль viewer по умолчанию, если нет других ролей
    if not db.user_has_role(user_id, 'viewer') and not db.user_has_role(user_id, 'admin') and not db.user_has_role(
            user_id, 'comedian'):
        db.add_role_to_user(user_id, 'viewer')


if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН И РАБОТАЕТ")
    print("=" * 50)

    # Получаем статистику базы данных
    stats = db.get_database_stats()

    print(f"📊 СТАТИСТИКА БАЗЫ ДАННЫХ:")
    print(f"👥 Всего пользователей: {stats['total_users']}")
    print(f"🎭 Всего ролей: {stats['total_roles']}")
    print(f"🔗 Всего назначений ролей: {stats['total_user_roles']}")
    print()
    print("📈 РАСПРЕДЕЛЕНИЕ ПО РОЛЯМ:")
    for role, count in stats['role_stats'].items():
        print(f"   {role}: {count} пользователей")

    admin_ids = db.get_users_with_role('admin')
    print()
    print(f"👑 АДМИНИСТРАТОРЫ: {admin_ids}")
    print("=" * 50)
    print("📝 Логирование активно. Все действия записываются в bot.log и bot_database.log")
    print("🔄 Бот готов к работе и ожидает сообщений...")
    print("=" * 50)

    bot.infinity_polling(timeout=10, long_polling_timeout=
