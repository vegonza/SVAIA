from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Project(db.Model):
    """Table for storing project information."""
    uuid: Mapped[str] = mapped_column(db.String(36), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    user: Mapped[str] = mapped_column(db.String(12), db.ForeignKey('user.username'), nullable=False)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name
        }


class User(db.Model):
    """Table for storing user information."""
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(12), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(12), nullable=False)
    project_uuid: Mapped[str] = mapped_column(db.String(36), db.ForeignKey('project.uuid'))
