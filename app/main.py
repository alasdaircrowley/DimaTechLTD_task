from sanic import Sanic
from sanic.exceptions import NotFound, InvalidUsage, Forbidden
from sanic.response import json

from .auth import authenticate_user, protected
from .config import SECRET_KEY
from .crud import create_user, get_users
from .models import db, User, Account, Payment, init_db
from .schemas import UserSchema, AccountSchema, PaymentSchema

app = Sanic("PaymentAPI")


@app.listener('before_server_start')
async def setup_db(app, loop):
    await db.set_bind("postgresql://postgres:postgres@db:5432/payment_db")
    await init_db()


@app.post("/auth")
async def auth(request):
    data = request.json
    if not data or "email" not in data or "password" not in data:
        raise InvalidUsage("Email and password are required")

    token = await authenticate_user(data["email"], data["password"])
    return json({"token": token})


@app.get("/me", middleware=[protected])
async def get_me(request):
    user = await User.get(request.ctx.user_id)
    if not user:
        raise NotFound("User not found")
    return json(UserSchema().dump(user))


@app.get("/accounts", middleware=[protected])
async def get_user_accounts(request):
    accounts = await Account.query.where(Account.user_id == request.ctx.user_id).gino.all()
    return json(AccountSchema(many=True).dump(accounts))


@app.get("/payments", middleware=[protected])
async def get_user_payments(request):
    payments = await Payment.query.where(Payment.user_id == request.ctx.user_id).gino.all()
    return json(PaymentSchema(many=True).dump(payments))


@app.post("/admin/auth")
async def admin_auth(request):
    data = request.json
    if not data or "email" not in data or "password" not in data:
        raise InvalidUsage("Email and password are required")

    token = await authenticate_user(data["email"], data["password"], admin=True)
    return json({"token": token})


@app.get("/admin/users", middleware=[protected])
async def admin_get_users(request):
    if not request.ctx.is_admin:
        raise Forbidden("Admin access required")
    users = await get_users()
    return json(UserSchema(many=True).dump(users))


@app.post("/admin/users", middleware=[protected])
async def admin_create_user(request):
    if not request.ctx.is_admin:
        raise Forbidden("Admin access required")

    if not request.json:
        raise InvalidUsage("User data is required")

    user = await create_user(request.json)
    return json(UserSchema().dump(user))


@app.post("/webhook/payment")
async def payment_webhook(request):
    if not request.json:
        raise InvalidUsage("Payment data is required")

    data = request.json
    required_fields = ["transaction_id", "account_id", "user_id", "amount", "signature"]
    if not all(field in data for field in required_fields):
        raise InvalidUsage(f"Required fields: {', '.join(required_fields)}")

    signature_str = f"{data['account_id']}{data['amount']}{data['transaction_id']}{data['user_id']}{SECRET_KEY}"
    import hashlib
    expected_signature = hashlib.sha256(signature_str.encode()).hexdigest()

    if data["signature"] != expected_signature:
        raise Forbidden("Invalid signature")

    user = await User.get(data["user_id"])
    if not user:
        raise NotFound("User not found")

    account = await Account.get(data["account_id"])
    if not account:
        account = await Account.create(
            id=data["account_id"],
            user_id=data["user_id"],
            balance=0
        )

    existing_payment = await Payment.query.where(Payment.transaction_id == data["transaction_id"]).gino.first()
    if existing_payment:
        raise InvalidUsage("Transaction already processed")

    payment = await Payment.create(
        transaction_id=data["transaction_id"],
        user_id=data["user_id"],
        account_id=data["account_id"],
        amount=data["amount"]
    )

    await account.update(balance=Account.balance + data["amount"]).apply()

    return json({"status": "success", "payment_id": payment.id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)