import sqlite3
import os
import logging as std_logging

# Настройка логирования
std_logging.basicConfig(
    level=std_logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        std_logging.StreamHandler(),
        std_logging.FileHandler('bot_database.log', encoding='utf-8')
    ]
)
logger = std_logging.getLogger('Database')

class Database:
    def __init__(self, db_name='bot_database.db'):
        self.db_name = db_name
        logger.info(f"Инициализация базы данных: {db_name}")
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        logger.info("Создание таблиц базы данных...")

        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица ролей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')

        # Таблица связи пользователей и ролей (many-to-many)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER,
            role_id INTEGER,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
        ''')

        # Вставляем стандартные роли, если их нет
        default_roles = ['admin', 'comedian', 'photo_sender', 'viewer']
        for role in default_roles:
            cursor.execute('INSERT OR IGNORE INTO roles (name) VALUES (?)', (role,))
            logger.info(f"Добавлена роль: {role}")

        # Добавляем администраторов по умолчанию
        default_admin_ids = [6586133062, 474130433]
        for admin_id in default_admin_ids:
            # Добавляем пользователя, если его нет
            cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (admin_id,))
            # Получаем ID роли admin
            cursor.execute('SELECT id FROM roles WHERE name = "admin"')
            admin_role_id = cursor.fetchone()[0]
            # Назначаем роль admin
            cursor.execute('INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)', (admin_id, admin_role_id))
            logger.info(f"Добавлен администратор по умолчанию: {admin_id}")

        conn.commit()
        conn.close()
        logger.info("База данных успешно инициализирована")

    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь
        cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (user_id,))
        user_exists = cursor.fetchone()[0] > 0

        if not user_exists:
            cursor.execute('INSERT INTO users (id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
                           (user_id, username, first_name, last_name))
            conn.commit()
            logger.info(f"Добавлен новый пользователь: ID={user_id}, username={username}, first_name={first_name}, last_name={last_name}")
        else:
            logger.info(f"Пользователь уже существует: ID={user_id}")

        conn.close()

    def user_has_role(self, user_id, role_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) 
        FROM user_roles ur 
        JOIN roles r ON ur.role_id = r.id 
        WHERE ur.user_id = ? AND r.name = ?
        ''', (user_id, role_name))
        result = cursor.fetchone()[0] > 0
        conn.close()

        logger.info(f"Проверка роли: user_id={user_id}, role={role_name}, result={result}")
        return result

    def add_role_to_user(self, user_id, role_name):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем ID роли
        cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
        role_result = cursor.fetchone()

        if role_result:
            role_id = role_result[0]

            # Проверяем, есть ли уже эта роль у пользователя
            cursor.execute('SELECT COUNT(*) FROM user_roles WHERE user_id = ? AND role_id = ?', (user_id, role_id))
            role_exists = cursor.fetchone()[0] > 0

            if not role_exists:
                cursor.execute('INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)', (user_id, role_id))
                conn.commit()
                logger.info(f"Добавлена роль пользователю: user_id={user_id}, role={role_name}")
            else:
                logger.info(f"Роль уже назначена: user_id={user_id}, role={role_name}")

        conn.close()

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, first_name, last_name FROM users')
        users = cursor.fetchall()
        conn.close()

        logger.info(f"Получен список всех пользователей: {len(users)} пользователей")
        return [user[0] for user in users]  # Возвращаем только ID

    def get_users_with_role(self, role_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT u.id, u.username, u.first_name, u.last_name
        FROM users u 
        JOIN user_roles ur ON u.id = ur.user_id 
        JOIN roles r ON ur.role_id = r.id 
        WHERE r.name = ?
        ''', (role_name,))
        users = cursor.fetchall()
        conn.close()

        logger.info(f"Получены пользователи с ролью '{role_name}': {len(users)} пользователей")
        return [user[0] for user in users]  # Возвращаем только ID

    def get_user_roles(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT r.name 
        FROM roles r 
        JOIN user_roles ur ON r.id = ur.role_id 
        WHERE ur.user_id = ?
        ''', (user_id,))
        roles = [row[0] for row in cursor.fetchall()]
        conn.close()

        logger.info(f"Получены роли пользователя: user_id={user_id}, roles={roles}")
        return roles

    def remove_role_from_user(self, user_id, role_name):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем ID роли
        cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
        role_result = cursor.fetchone()

        if role_result:
            role_id = role_result[0]
            cursor.execute('DELETE FROM user_roles WHERE user_id = ? AND role_id = ?', (user_id, role_id))
            conn.commit()
            logger.info(f"Удалена роль у пользователя: user_id={user_id}, role={role_name}")

        conn.close()

    def get_database_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем статистику
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM roles')
        total_roles = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM user_roles')
        total_user_roles = cursor.fetchone()[0]

        # Получаем количество пользователей по ролям
        role_stats = {}
        cursor.execute('''
        SELECT r.name, COUNT(ur.user_id) 
        FROM roles r 
        LEFT JOIN user_roles ur ON r.id = ur.role_id 
        GROUP BY r.name
        ''')
        for role_name, count in cursor.fetchall():
            role_stats[role_name] = count

        conn.close()

        stats = {
            'total_users': total_users,
            'total_roles': total_roles,
            'total_user_roles': total_user_roles,
            'role_stats': role_stats
        }

        logger.info(f"Статистика базы данных: {stats}")
        return stats

# Создаем глобальный экземпляр базы данных
db = Database()