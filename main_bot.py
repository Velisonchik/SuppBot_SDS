import asyncio
import threading

from time import sleep
from ad import get_ids_from_ad
from support import create_new_issue
from reqs import BOT_TOKEN, HELP_TEXT_FOR_BOT
from aiogram import Bot, Dispatcher, enums
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ContentType


# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher()

# Словарь, в котором будут храниться данные пользователя
allow_ids = {}
users_dict = {}


def parse_msg(mas):
    d = dict()
    for i in mas:
        if 't=' in i.lower() or 'j=' in i.lower() or 'a=' in i:
            d[i[:i.index('=')].lower()] = i[i.index('=') + 1:].lower()
            mas[mas.index(i)] = ''
    d['text'] = ' '.join(mas).strip()
    return d


'''@dp.message()
async def message_for_all(message: Message):
    global allow_ids
    print(message)
    users_dict[message.from_user.id] = parse_msg(message.text.split())'''


@dp.message(Command(commands=['help']))
async def help_message(message: Message):
    global allow_ids
    await message.answer(HELP_TEXT_FOR_BOT, parse_mode=enums.parse_mode.ParseMode.HTML)


@dp.message(lambda x: x.content_type != ContentType.TEXT)
async def not_text(message: Message):
    global allow_ids
    users_dict[message.from_user.id] = {}
    await message.reply('Почитай пожалуйста /help, я просил не присылать мне какие-либо вложения.\nСпасибо.')


@dp.message(lambda x: str(x.from_user.id) in allow_ids and x.forward_from)
async def adding_text_from_forward(message: Message):
    try:
        global allow_ids
        if 'text' in users_dict[message.from_user.id].keys():
            users_dict[message.from_user.id]['comment'] = users_dict[message.from_user.id]['text']
            users_dict[message.from_user.id]['text'] = ''
        if 'j' in users_dict[message.from_user.id].keys() and 't' in users_dict[message.from_user.id].keys():
            await message.answer('Понял что есть форвард.')
            users_dict[message.from_user.id]['text'] = message.text
            users_dict[message.from_user.id]['forward_user_id'] = message.forward_from.id

            if str(users_dict[message.from_user.id]['forward_user_id']) in allow_ids:
                username_from_ad = allow_ids[str(users_dict[message.from_user.id]['forward_user_id'])]
            elif 'a' in users_dict[message.from_user.id].keys():
                username_from_ad = users_dict[message.from_user.id]['a']
            else:
                username_from_ad = allow_ids[str(message.from_user.id)]

            print(users_dict)
            await message.reply(
                create_new_issue(subject=users_dict[message.from_user.id]['text'][:254],
                                 description=users_dict[message.from_user.id]['text'],
                                 username=allow_ids[str(message.from_user.id)],
                                 tracker_id_in_str=users_dict[message.from_user.id]['j'],
                                 elapsed_time=float(users_dict[message.from_user.id]['t']),
                                 author_issue=username_from_ad, comment=users_dict[message.from_user.id]['comment']))
            users_dict[message.from_user.id] = {}
        else:
            await message.answer('Не указаны t или j. Попробуй еще раз.')
            users_dict[message.from_user.id] = {}
    except Exception as e:
        print(e)
        await message.answer('Не вышло, надо смотреть логи.')
        users_dict[message.from_user.id] = {}


@dp.message(lambda x: str(x.from_user.id) in allow_ids and 't=' in x.text.lower() and 'j=' in x.text.lower())
async def first_create_issue(message: Message):
    try:
        users_dict[message.from_user.id] = {}
        users_dict[message.from_user.id] = parse_msg(message.text.split())
        print(users_dict)
        if users_dict[message.from_user.id]['text']:
            if len(users_dict[message.from_user.id]) >= 2 and \
                    users_dict[message.from_user.id]['t'].replace(".", "").isnumeric() and \
                    users_dict[message.from_user.id]['j'].isalpha():
                await message.answer('Завожу задачу, подожди.')
                await asyncio.sleep(2)
                if 'comment' not in users_dict[message.from_user.id].keys() \
                        and 'text' in users_dict[message.from_user.id]:
                    await message.reply(
                        create_new_issue(subject=users_dict[message.from_user.id]['text'][:254],
                                         description=users_dict[message.from_user.id]['text'],
                                         username=allow_ids[str(message.from_user.id)],
                                         tracker_id_in_str=users_dict[message.from_user.id]['j'],
                                         elapsed_time=float(users_dict[message.from_user.id]['t']),
                                         author_issue=users_dict[message.from_user.id]['a']
                                         if 'a' in users_dict[message.from_user.id].keys() else ''))
                users_dict[message.from_user.id] = {}
            else:
                await message.answer('Я тебя не понимаю.')
        else:
            await message.answer('Я хочу еще текст.')
    except Exception as e:
        print(e)
        await message.answer('Не вышло, надо смотреть логи.')
        users_dict[message.from_user.id] = {}


@dp.message(lambda x: str(x.from_user.id) in allow_ids and ('t=' not in x.text or 'j=' not in x.text))
async def message_withou_t_or_j(message: Message):
    users_dict[message.from_user.id] = {}
    await message.reply("В твоем сообщении отсутсвует 't=' или 'j='.")


@dp.message(lambda x: str(x.from_user.id) not in allow_ids)
async def message_for_all(message: Message):
    global allow_ids
    users_dict[message.from_user.id] = {}
    await message.reply("Я тебя не знаю, пройди аутентификацю у @sds_corp_bot, и возвращайся!")


def update_allow_ids():
    global allow_ids
    while True:
        allow_ids = get_ids_from_ad()
        # print(allow_ids)
        sleep(2)


if __name__ == '__main__':
    # asyncio.run(update_allow_ids())
    updating_IDS = threading.Thread(target=update_allow_ids, args=(), daemon=True)
    updating_IDS.start()
    dp.run_polling(bot)
