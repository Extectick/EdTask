from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer, Boolean, DateTime, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy import create_engine

class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///data/base.db", echo=False)
Session = sessionmaker(bind=engine)


class MasterUser(Base):
    __tablename__ = "masters"
    master_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)

    # Связи: Мастер владеет ролями, учениками и задачами
    owned_roles: Mapped[List["Role"]] = relationship(back_populates="creator")
    apprentices: Mapped[List["Apprentice"]] = relationship(back_populates="master")
    tasks: Mapped[List["Task"]] = relationship(back_populates="teacher")

class Role(Base):
    __tablename__ = "role_names"
    role_id: Mapped[str] = mapped_column(String, primary_key=True)
    role_name: Mapped[str] = mapped_column(String, nullable=False)
    # Роль теперь привязана к учителю
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.master_id"))
    
    creator: Mapped["MasterUser"] = relationship(back_populates="owned_roles")

class User(Base): # Оставим логику User для учеников
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String)
    
    # Получение ролей через таблицу связей
    user_roles: Mapped[List["UserRole"]] = relationship()

    def get_active_tasks(self, session):
        """Метод получения активных задач (от новых к старым)"""
        user_role_ids = [r.role_id for r in self.user_roles]
        stmt = (
            select(Task)
            .distinct()
            .outerjoin(TaskAccessUser)
            .outerjoin(TaskAccessRole)
            .where(Task.is_active == True)
            .where(
                (TaskAccessUser.user_id == self.user_id) | 
                (TaskAccessRole.role_id.in_(user_role_ids))
            )
            .order_by(Task.created_at.desc())
        )
        return session.execute(stmt).scalars().all()

class Apprentice(Base):
    __tablename__ = "apprentices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.master_id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    
    master: Mapped["MasterUser"] = relationship(back_populates="apprentices")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("masters.master_id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    teacher: Mapped["MasterUser"] = relationship(back_populates="tasks")
    images: Mapped[List["TaskImage"]] = relationship(back_populates="task")
    answers: Mapped[List["Answer"]] = relationship(back_populates="task")
    
    # Связи для доступа к задаче
    access_users: Mapped[List["TaskAccessUser"]] = relationship(back_populates="task")
    access_roles: Mapped[List["TaskAccessRole"]] = relationship(back_populates="task")


class TaskImage(Base):
    __tablename__ = "task_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"), nullable=True)
    image_name: Mapped[str] = mapped_column(String)

    task: Mapped["Task"] = relationship(back_populates="images")
    answer: Mapped["Answer"] = relationship(back_populates="images")


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    text: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task: Mapped["Task"] = relationship(back_populates="answers")
    user: Mapped["User"] = relationship()
    images: Mapped[List["TaskImage"]] = relationship(back_populates="answer")


class UserRole(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    role_id: Mapped[str] = mapped_column(ForeignKey("role_names.role_id"))

class TaskAccessUser(Base):
    __tablename__ = "task_access_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    
    task: Mapped["Task"] = relationship(back_populates="access_users")
    user: Mapped["User"] = relationship()


class TaskAccessRole(Base):
    __tablename__ = "task_access_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    role_id: Mapped[str] = mapped_column(ForeignKey("role_names.role_id"))
    
    task: Mapped["Task"] = relationship(back_populates="access_roles")
    role: Mapped["Role"] = relationship()

def init_db():
    Base.metadata.create_all(engine)