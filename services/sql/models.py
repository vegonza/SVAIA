from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class Project(db.Model):
    uuid: Mapped[str] = mapped_column(db.String(36), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=True)
    vulnerability_level: Mapped[str] = mapped_column(db.Text, nullable=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='project', lazy=True, cascade="all, delete-orphan")
    dockerfiles = db.relationship('Dockerfile', backref='project', lazy=True, cascade="all, delete-orphan")
    docker_composes = db.relationship('DockerCompose', backref='project', lazy=True, cascade="all, delete-orphan")
    sboms = db.relationship('SoftwareBillOfMaterials', backref='project', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'vulnerability_level': self.vulnerability_level,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Dockerfile(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    project_uuid: Mapped[str] = mapped_column(db.String(36), db.ForeignKey('project.uuid'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'project_uuid': self.project_uuid,
        }


class DockerCompose(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    project_uuid: Mapped[str] = mapped_column(db.String(36), db.ForeignKey('project.uuid'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'project_uuid': self.project_uuid
        }


class SoftwareBillOfMaterials(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    project_uuid: Mapped[str] = mapped_column(db.String(36), db.ForeignKey('project.uuid'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'project_uuid': self.project_uuid
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


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        }
