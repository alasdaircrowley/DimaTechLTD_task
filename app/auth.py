import jwt
from datetime import datetime, timedelta
from sanic.exceptions import Unauthorized
from .models import User
from .config import SECRET_KEY


async def authenticate_user(email, password, admin=False):
    if not email or not password:
        raise Unauthorized("Email and password are required")

    user = await User.query.where(User.email == email).gino.first()
    if not user or user.password != password:
        raise Unauthorized("Invalid credentials")

    if admin and not user.is_admin:
        raise Unauthorized("Admin access required")

    payload = {
        "user_id": user.id,
        "is_admin": user.is_admin,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


async def protected(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Unauthorized("Invalid token")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.ctx.user_id = payload["user_id"]
        request.ctx.is_admin = payload["is_admin"]
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token expired")
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token")