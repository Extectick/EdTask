#!/usr/bin/env python3
"""Проверка пользователей в PostgreSQL."""

from sqlalchemy.orm import aliased

from data.data import Session, User, init_db


init_db()

with Session() as session:
    print("=" * 60)
    print("ПОЛЬЗОВАТЕЛИ:")
    print("=" * 60)
    users = session.query(User).order_by(User.id).all()
    for user in users:
        print(
            f"ID: {user.id}, Token: {user.token}, Имя: {user.full_name}, "
            f"Мастер: {user.is_master}, ID мастера: {user.master_id}"
        )

    print("\n" + "=" * 60)
    print("МАСТЕРА (is_master=True):")
    print("=" * 60)
    masters = session.query(User).filter(User.is_master.is_(True)).order_by(User.id).all()
    for master in masters:
        print(f"ID: {master.id}, Token: {master.token}, Имя: {master.full_name}")

    print("\n" + "=" * 60)
    print("УЧЕНИКИ (is_master=False):")
    print("=" * 60)
    master_alias = aliased(User)
    students = (
        session.query(User, master_alias.token)
        .outerjoin(master_alias, User.master_id == master_alias.id)
        .filter(User.is_master.is_(False))
        .order_by(User.id)
        .all()
    )
    for student, master_token in students:
        print(
            f"ID: {student.id}, Token: {student.token}, Имя: {student.full_name}, "
            f"ID мастера: {student.master_id}, Токен мастера: {master_token}"
        )
