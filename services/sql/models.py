from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Project(db.Model):
    uuid: Mapped[str] = mapped_column(db.String(36), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    # TODO: change to nullable=False
    user_id: Mapped[str] = mapped_column(db.String(12), db.ForeignKey('user.id'), nullable=True)
    messages = db.relationship('Message', backref='project', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name
        }


class Message(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    is_user: Mapped[bool] = mapped_column(db.Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    project_uuid: Mapped[str] = mapped_column(db.String(36), db.ForeignKey('project.uuid'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'is_user': self.is_user,
            'timestamp': self.timestamp.isoformat(),
            'project_uuid': self.project_uuid
        }


class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(db.String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(db.String(50), nullable=True)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(db.String(12), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(12), nullable=False)
