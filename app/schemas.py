from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Str()
    password = fields.Str()

class AccountSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    balance = fields.Decimal()

class PaymentSchema(Schema):
    id = fields.Int()
    transaction_id = fields.Str()
    user_id = fields.Int()
    account_id = fields.Int()
    amount = fields.Decimal()
    