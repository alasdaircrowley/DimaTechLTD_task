from .models import User, Account

async def create_user(user_data):
    return await User.create(**user_data)

async def get_users():
    return await User.query.gino.all()

async def get_user(user_id):
    return await User.get(user_id)

async def update_user(user_id, user_data):
    user = await User.get(user_id)
    await user.update(**user_data).apply()
    return user
async def delete_user(user_id):
    user = await User.get(user_id)
    await user.delete()
    return {"status": "deleted"}

