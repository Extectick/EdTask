#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания пользователей-мастеров вручную.

Использование:
    python create_master.py <token> <full_name>

Пример:
    python create_master.py master_token_123 "Иван Петрович Петров"
"""

import sys
import os

# Добавляем путь к backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.data import Session, User, init_db

init_db()

def create_master(token: str, full_name: str):
    """Создаёт пользователя с правами мастера."""
    with Session() as session:
        # Проверяем, нет ли уже такого пользователя
        existing = session.query(User).filter(User.token == token).first()
        if existing:
            print(f"ERROR: User with token '{token}' already exists!")
            print(f"   ID: {existing.id}")
            return False

        # Создаём мастера
        master = User(
            token=token,
            full_name=full_name,
            is_master=True,
            master_id=None
        )
        session.add(master)
        session.commit()
        session.refresh(master)

        print(f"SUCCESS: Master created!")
        print(f"   ID: {master.id}")
        print(f"   Token: {master.token}")
        print(f"   Name: {master.full_name}")
        print(f"\nUse token '{master.token}' to login as master.")
        
        return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python create_master.py <token> <full_name>")
        print("\nExamples:")
        print('  python create_master.py master123 Ivan_Petrov')
        print('  python create_master.py teacher_smith John_Smith')
        print("\nNote: Use underscores instead of spaces in names")
        print("DATABASE_URL must point to PostgreSQL.")
        sys.exit(1)

    token = sys.argv[1]
    full_name = sys.argv[2]

    # Проверка токена
    if len(token) < 3:
        print("ERROR: Token must be at least 3 characters!")
        sys.exit(1)

    if not full_name.strip():
        print("ERROR: Name cannot be empty!")
        sys.exit(1)

    create_master(token, full_name)


if __name__ == "__main__":
    main()
