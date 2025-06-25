from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
import sqlalchemy as sa
from gino import Gino
db = Gino()

class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    is_admin = Column(sa.Boolean, default=False)

class Account(db.Model):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    balance = Column(Numeric(10, 2), default=0)

class Payment(db.Model):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(100), unique=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Numeric(10, 2))

async def init_db():
    await db.gino.create_all()
    await User.create(
        email="user@example.com",
        password="user123",
        full_name="Test User",
        is_admin=False
    )

    await User.create(
        email="admin@example.com",
        password="admin123",
        full_name="Admin User",
        is_admin=True
    )