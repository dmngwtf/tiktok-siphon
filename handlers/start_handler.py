from utils.logger import logger
from aiogram import types

async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"/start from user={user_id}")
    await message.answer(
        "Привет! Кидай ссылку на TikTok — скачаю видео **без водяного знака**."
    )


