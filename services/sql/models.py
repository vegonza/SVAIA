from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

class Project(db.Model):
    """Table for storing project information."""
    uuid: Mapped[str] = mapped_column(db.String(36), primary_key=True, nullable= False)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    user: Mapped[str] = mapped_column(db.String(12), db.ForeignKey('user.username'), nullable=False)

class User(db.Model):
    """Table for storing user information."""
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(12), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(12), nullable=False)
    rol: Mapped[str] = mapped_column(db.String(12), nullable=False)
    

with app.app_context():
    db.create_all()