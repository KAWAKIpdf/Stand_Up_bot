import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7775082164:AAHovLa3Q-4906rtycSTbJ-_PgAkxwLVve8'
ADMIN_IDS = {6586133062}  # Множество админов
bot = telebot.TeleBot(TOKEN)

comedians_list = "1. Жуков Дима\n"
censorship_rules = "Избегайте тем: религия, политика, дискриминация."
allowed_photo_users = set()
registered_users = set()


@bot.message_handler(commands=['start'])
def start(message):
    registered_users.add(message.chat.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👀 Я зритель", callback_data="viewer"))
    markup.add(InlineKeyboardButton("🎤 Я новый комик", callback_data="new_comedian"))
    markup.add(InlineKeyboardButton("💼 Я спонсор", callback_data="sponsor"))
    markup.add(InlineKeyboardButton("☕️ Онлайн-заказ в 6ки", callback_data="order"))
    if message.from_user.id in ADMIN_IDS:
        markup.add(InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin"))
    bot.send_message(message.chat.id, "Привет! Кто ты?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "viewer":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 Список комиков", callback_data="comedians"))
        markup.add(InlineKeyboardButton("🗓 Расписание", callback_data="schedule"))
        markup.add(InlineKeyboardButton("🔗 Наши соцсети", callback_data="socials"))
        bot.send_message(call.message.chat.id, "Меню для зрителей:", reply_markup=markup)

    elif call.data == "new_comedian":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📜 Правила и цензура", callback_data="rules"))
        markup.add(InlineKeyboardButton("📘 Как стать комиком", callback_data="how"))
        markup.add(InlineKeyboardButton("🌟 Напутствие", callback_data="wish"))
        bot.send_message(call.message.chat.id, "Меню для комиков:", reply_markup=markup)

    elif call.data == "sponsor":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🚀 О нас", callback_data="about"))
        markup.add(InlineKeyboardButton("📸 Где выступали", callback_data="places"))
        markup.add(InlineKeyboardButton("📞 Контакты", callback_data="contacts"))
        bot.send_message(call.message.chat.id, "Меню для спонсоров:", reply_markup=markup)

    elif call.data == "admin" and call.from_user.id in ADMIN_IDS:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📝 Редактировать комиков", callback_data="edit_comedians"))
        markup.add(InlineKeyboardButton("🛡 Редактировать правила", callback_data="edit_rules"))
        markup.add(InlineKeyboardButton("➕ Добавить фото-автора", callback_data="add_photo"))
        markup.add(InlineKeyboardButton("👑 Назначить администратора", callback_data="add_admin"))
        bot.send_message(call.message.chat.id, "⚙️ Админ-панель:", reply_markup=markup)

    elif call.data == "comedians":
        bot.send_message(call.message.chat.id, comedians_list)
    elif call.data == "schedule":
        bot.send_message(call.message.chat.id, "📅 31 августа, 19:00\n🕒 Тайминг:\n18:30 сбор гостей\n19:00 начало\n21:00 финал")
    elif call.data == "socials":
        bot.send_message(call.message.chat.id, "🔗 ВКонтакте: https://vk.com/yourgroup")
    elif call.data == "rules":
        bot.send_message(call.message.chat.id, censorship_rules)
    elif call.data == "how":
        bot.send_message(call.message.chat.id, "1. Напиши нам в бот\n2. Пройди короткую репетицию\n3. Получи слот на выступление!")
    elif call.data == "wish":
        bot.send_message(call.message.chat.id, "✨ Помни: тишина — это часть шоу. Будь собой и получай кайф!")
    elif call.data == "order":
        bot.send_message(call.message.chat.id, "☕️ Онлайн-заказ в 6ки доступен всем — [меню здесь](https://menu-link.com)", parse_mode="Markdown")
    elif call.data == "about":
        bot.send_message(call.message.chat.id, "Мы — Физтех Stand_up клуб. Были на ВК Фесте.")
    elif call.data == "places":
        bot.send_message(call.message.chat.id, "📍 ВК Фест\n📍 Клуб 6ки")
    elif call.data == "contacts":
        bot.send_message(call.message.chat.id, "📧@kostyastrong")
    elif call.data == "edit_comedians":
        msg = bot.send_message(call.message.chat.id, "✏️ Отправьте новый список комиков:")
        bot.register_next_step_handler(msg, save_comedians)
    elif call.data == "edit_rules":
        msg = bot.send_message(call.message.chat.id, "✏️ Отправьте новые правила цензуры:")
        bot.register_next_step_handler(msg, save_rules)
    elif call.data == "add_photo":
        msg = bot.send_message(call.message.chat.id, "Отправьте @username или ID пользователя:")
        bot.register_next_step_handler(msg, save_photo_user)
    elif call.data == "add_admin":
        msg = bot.send_message(call.message.chat.id, "Отправьте username нового администратора:")
        bot.register_next_step_handler(msg, save_admin)

def save_comedians(message):
    global comedians_list
    comedians_list = message.text
    bot.send_message(message.chat.id, "✅ Список комиков обновлён.")

def save_rules(message):
    global censorship_rules
    censorship_rules = message.text
    bot.send_message(message.chat.id, "✅ Правила обновлены.")

def save_photo_user(message):
    try:
        if message.text.startswith("@"):  # username
            allowed_photo_users.add(message.text[1:])
        else:  # user_id
            allowed_photo_users.add(int(message.text))
        bot.send_message(message.chat.id, "✅ Пользователь добавлен в список авторов фото.")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка. Проверь формат ID или username.")

def save_admin(message):
    username = message.text.strip()
    if username.startswith('@'):
        username = username[1:]

        try:
            # Пытаемся получить информацию о пользователе по username
            user_info = bot.get_chat_member(message.chat.id, username)
            if user_info.user.id:
                new_admin_id = user_info.user.id
                ADMIN_IDS.add(new_admin_id)
                bot.send_message(message.chat.id, f"✅ Пользователь @{username} назначен админом.")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка. Этот пользователь не найден.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {e}. Этот пользователь не найден или произошла ошибка при получении данных.")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка. Введите корректный username с @.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user = message.from_user
    if user.id in ADMIN_IDS or user.username in allowed_photo_users or user.id in allowed_photo_users:
        bot.send_message(message.chat.id, "✅ Фото получено. Рассылаю всем пользователям...")
        for user_id in registered_users:
            try:
                bot.send_photo(user_id, message.photo[-1].file_id, caption="🔞 Новое фото с мероприятия!")
            except:
                continue
    else:
        bot.send_message(message.chat.id, "🚫 У вас нет прав публиковать фото.")

bot.polling()
