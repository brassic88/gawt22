import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица слотов (расписания)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            is_booked INTEGER DEFAULT 0,
            user_id INTEGER DEFAULT NULL,
            user_name TEXT DEFAULT NULL,
            user_phone TEXT DEFAULT NULL
        )""")
        self.connection.commit()

    # --- Методы для пользователя ---
    def get_available_dates(self):
        self.cursor.execute("SELECT DISTINCT date FROM slots WHERE is_booked = 0 AND date >= ?", (datetime.now().strftime("%Y-%m-%d"),))
        return [row[0] for row in self.cursor.fetchall()]

    def get_available_times(self, date):
        self.cursor.execute("SELECT id, time FROM slots WHERE date = ? AND is_booked = 0", (date,))
        return self.cursor.fetchall()

    def check_user_booking(self, user_id):
        self.cursor.execute("SELECT id FROM slots WHERE user_id = ? AND is_booked = 1", (user_id,))
        return self.cursor.fetchone()

    def book_slot(self, slot_id, user_id, name, phone):
        self.cursor.execute("UPDATE slots SET is_booked = 1, user_id = ?, user_name = ?, user_phone = ? WHERE id = ?",
                           (user_id, name, phone, slot_id))
        self.connection.commit()

    def get_user_booking(self, user_id):
        self.cursor.execute("SELECT id, date, time FROM slots WHERE user_id = ? AND is_booked = 1", (user_id,))
        return self.cursor.fetchone()

    def cancel_booking(self, slot_id):
        self.cursor.execute("UPDATE slots SET is_booked = 0, user_id = NULL, user_name = NULL, user_phone = NULL WHERE id = ?", (slot_id,))
        self.connection.commit()

    # --- Методы администратора ---
    def add_slot(self, date, time):
        self.cursor.execute("INSERT INTO slots (date, time) VALUES (?, ?)", (date, time))
        self.connection.commit()

    def delete_slot(self, slot_id):
        self.cursor.execute("DELETE FROM slots WHERE id = ?", (slot_id,))
        self.connection.commit()

    def get_all_slots_by_date(self, date):
        self.cursor.execute("SELECT id, time, is_booked, user_name FROM slots WHERE date = ?", (date,))
        return self.cursor.fetchall()

    def close_day(self, date):
        self.cursor.execute("DELETE FROM slots WHERE date = ?", (date,))
        self.connection.commit()

    def get_slot_by_id(self, slot_id):
        self.cursor.execute("SELECT * FROM slots WHERE id = ?", (slot_id,))
        return self.cursor.fetchone()

    def get_all_active_bookings(self):
        # Для восстановления шедулера
        self.cursor.execute("SELECT id, date, time, user_id FROM slots WHERE is_booked = 1")
        return self.cursor.fetchall()

db = Database("manicure.db")