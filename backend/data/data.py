import os
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required. Configure PostgreSQL connection before starting backend.")
    return database_url


engine = create_engine(get_database_url(), echo=False, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String)
    is_master: Mapped[bool] = mapped_column(Boolean, default=False)
    master_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Связь с мастером (для учеников)
    master: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[id],
        back_populates="apprentices"
    )

    # Связь с учениками (для мастеров)
    apprentices: Mapped[List["User"]] = relationship(
        "User",
        back_populates="master",
        foreign_keys=[master_id]
    )


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    master_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.token"))  # Ученик, которому назначена задача
    able_answer: Mapped[bool] = mapped_column(Boolean, default=True)

    # Ответы на задачу
    answers: Mapped[List["Answer"]] = relationship(
        "Answer",
        back_populates="task"
    )


class TaskImage(Base):
    __tablename__ = "task_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    answer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("answers.id"), nullable=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))


class TaskFile(Base):
    __tablename__ = "task_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.token"))  # Токен ученика
    content: Mapped[str] = mapped_column(String)
    image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("images.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    comment_grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    task: Mapped["Task"] = relationship(back_populates="answers")


class AnswerImage(Base):
    __tablename__ = "answer_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String)
    original_name: Mapped[str] = mapped_column(String)  # Оригинальное имя файла


class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String)


def init_db():
    Base.metadata.create_all(engine)


def ensure_bootstrap_master():
    token = os.getenv("BOOTSTRAP_MASTER_TOKEN", "").strip()
    full_name = os.getenv("BOOTSTRAP_MASTER_FULL_NAME", "").strip()

    if not token or not full_name:
        return None

    with Session() as session:
        existing = session.query(User).filter(User.token == token).first()
        if existing:
            return existing

        master = User(
            token=token,
            full_name=full_name,
            is_master=True,
            master_id=None,
        )
        session.add(master)
        session.commit()
        session.refresh(master)
        return master
