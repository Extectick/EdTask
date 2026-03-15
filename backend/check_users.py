#!/usr/bin/env python3
"""Проверка пользователей в БД"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "base.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("ПОЛЬЗОВАТЕЛИ:")
print("=" * 60)
cursor.execute("SELECT id, token, full_name, is_master, master_id FROM users")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Token: {row[1]}, Имя: {row[2]}, Мастер: {bool(row[3])}, ID мастера: {row[4]}")

print("\n" + "=" * 60)
print("МАСТЕРА (is_master=1):")
print("=" * 60)
cursor.execute("SELECT id, token, full_name FROM users WHERE is_master = 1")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Token: {row[1]}, Имя: {row[2]}")

print("\n" + "=" * 60)
print("УЧЕНИКИ (is_master=0):")
print("=" * 60)
cursor.execute("""
    SELECT u.id, u.token, u.full_name, u.master_id, m.token as master_token 
    FROM users u 
    LEFT JOIN users m ON u.master_id = m.id 
    WHERE u.is_master = 0
""")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Token: {row[1]}, Имя: {row[2]}, ID мастера: {row[3]}, Токен мастера: {row[4]}")

conn.close()
