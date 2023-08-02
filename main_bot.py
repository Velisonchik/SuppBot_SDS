import asyncio
import logging
import threading
from pprint import pprint

from time import sleep
from ad import get_ids_from_ad
from support import create_new_issue
from reqs import BOT_TOKEN, HELP_TEXT_FOR_BOT
from aiogram import Bot, Dispatcher, enums
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ContentType

logging.basicConfig(level=logging.INFO, filename="SuppBot.log", format="%(asctime)s %(levelname)s %(module)s:%(lineno)s"
                                                                       " %(message)s")

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
    d['t'] = d['t'].replace(',', '.')
    return d


'''@dp.message()
async def message_for_all(message: Message):
    global allow_ids
    print(message)
    users_dict[message.from_user.id] = parse_msg(message.text.split())'''


@dp.message(Command(commands=['help']))
async def help_message(message: Message):
    global allow_ids
    logging.info(f'{message.from_user.id} send command HELP')
    await message.answer(HELP_TEXT_FOR_BOT, parse_mode=enums.parse_mode.ParseMode.HTML)


@dp.message(lambda x: x.content_type not in (ContentType.DOCUMENT, ContentType.TEXT, ContentType.PHOTO))
async def not_text(message: Message):
    global allow_ids
    pprint(message)
    logging.warning(f'{message.from_user.id, message.content_type} send message ANOTHER type')
    users_dict[message.from_user.id] = {}
    await message.reply('Почитай пожалуйста /help, я просил не присылать мне какие-либо вложения.\nСпасибо.')


@dp.message(lambda x: str(x.from_user.id) in allow_ids and x.forward_from and 'text' in users_dict[x.from_user.id])
async def adding_text_from_forward(message: Message):
    global allow_ids
    users_dict[message.from_user.id]['is_forward'] = True
    try:
        if 'text' in users_dict[message.from_user.id].keys():
            users_dict[message.from_user.id]['comment'] = users_dict[message.from_user.id]['text']
            users_dict[message.from_user.id]['text'] = ''
        if 'j' in users_dict[message.from_user.id].keys() and 't' in users_dict[message.from_user.id].keys():
            await message.answer('Понял что есть форвард.')

            if message.caption:
                users_dict[message.from_user.id]['text'] = message.caption
            elif message.text:
                users_dict[message.from_user.id]['text'] = message.text
            elif users_dict[message.from_user.id]['comment'] != '':
                users_dict[message.from_user.id]['text'] = users_dict[message.from_user.id]['comment']
                users_dict[message.from_user.id]['comment'] = ''
            else:
                users_dict[message.from_user.id]['text'] = ''
                await message.answer('Тема не может быть пустой. Попробуй еще раз.')

            if message.content_type == ContentType.PHOTO:
                await bot.download(message.photo[-1], f'{message.photo[-1].file_unique_id}.jpg')
                users_dict[message.from_user.id]['file_path'] = f'{message.photo[-1].file_unique_id}.jpg'

            elif message.content_type == ContentType.DOCUMENT:
                await bot.download(message.document, message.document.file_name)
                users_dict[message.from_user.id]['file_path'] = message.document.file_name

            users_dict[message.from_user.id]['forward_user_id'] = message.forward_from.id

            if str(users_dict[message.from_user.id]['forward_user_id']) in allow_ids:
                username_from_ad = allow_ids[str(users_dict[message.from_user.id]['forward_user_id'])]
            elif 'a' in users_dict[message.from_user.id].keys():
                username_from_ad = users_dict[message.from_user.id]['a']
            else:
                username_from_ad = allow_ids[str(message.from_user.id)]

            print(users_dict)
            logging.info(f'Issue INIT WITH FORWARD {users_dict[message.from_user.id]}')
            users_dict[message.from_user.id]['issue_URI'] = create_new_issue(
                subject=users_dict[message.from_user.id]['text'][:254],
                description=users_dict[message.from_user.id]['text'],
                username=allow_ids[str(message.from_user.id)],
                tracker_id_in_str=users_dict[message.from_user.id]['j'],
                elapsed_time=float(users_dict[message.from_user.id]['t']),
                author_issue=username_from_ad, comment=users_dict[message.from_user.id]['comment'],
                file_path='' if 'file_path' not in users_dict[message.from_user.id].keys() else
                users_dict[message.from_user.id]['file_path']
            )
            await message.reply(users_dict[message.from_user.id]['issue_URI'])
            logging.info(f"Issue CREATED WITH FORWARD {users_dict[message.from_user.id]}")
            users_dict[message.from_user.id] = {}
        else:
            await message.answer('Не указаны t или j. Попробуй еще раз.')
            logging.warning(f'Error in checking t AND j items {users_dict[message.from_user.id]}')
            users_dict[message.from_user.id] = {}
    except Exception as e:
        print(e)
        logging.critical({users_dict[message.from_user.id]}, exc_info=True)
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
                    logging.info(f'Issue INIT WO forward {users_dict[message.from_user.id]}')
                    users_dict[message.from_user.id]['issue_URI'] = create_new_issue(
                        subject=users_dict[message.from_user.id]['text'][:254],
                        description=users_dict[message.from_user.id]['text'],
                        username=allow_ids[str(message.from_user.id)],
                        tracker_id_in_str=users_dict[message.from_user.id]['j'],
                        elapsed_time=float(users_dict[message.from_user.id]['t']),
                        author_issue=users_dict[message.from_user.id]['a']
                        if 'a' in users_dict[message.from_user.id].keys() else '')
                    await message.reply(users_dict[message.from_user.id]['issue_URI'])
                    logging.info(f'Issue CREATED {users_dict[message.from_user.id]}')
                    users_dict[message.from_user.id] = {}
            else:
                await message.answer('Я тебя не понимаю. Попробуй еще раз.')
                logging.warning(f'Error in checking len items {users_dict[message.from_user.id]}')
                users_dict[message.from_user.id] = {}
        else:
            logging.warning(f'Error in checking TEXT items {users_dict[message.from_user.id]}')
            await asyncio.sleep(2)
            if 'is_forward' not in users_dict[message.from_user.id].keys():
                await message.answer('Я хочу еще текст. Попробуй еще раз.')
                users_dict[message.from_user.id] = {}
    except Exception as e:
        print(e)
        await message.answer('Не вышло, надо смотреть логи.')
        logging.critical({users_dict[message.from_user.id]}, exc_info=True)
        users_dict[message.from_user.id] = {}


@dp.message(lambda x: str(x.from_user.id) in allow_ids and ('t=' not in x.text or 'j=' not in x.text))
async def message_without_t_or_j(message: Message):
    users_dict[message.from_user.id] = {}
    logging.warning(f'{message.from_user.id, message.content_type} send message WITHOUT j= OR t=')
    await message.reply("В твоем сообщении отсутсвует 't=' или 'j='.")


@dp.message(lambda x: str(x.from_user.id) not in allow_ids)
async def message_for_all(message: Message):
    global allow_ids
    users_dict[message.from_user.id] = {}
    logging.warning(
        f'User ID {message.from_user.id}:{message.from_user.username} {message.from_user.first_name}:'
        f'{message.from_user.last_name} not in ALLOWED')
    await message.reply("Я тебя не знаю, пройди аутентификацю у @sds_corp_bot, и возвращайся!")


def update_allow_ids():
    global allow_ids
    while True:
        try:
            allow_ids = get_ids_from_ad()
            # print(allow_ids)
            sleep(2)
            logging.debug(f'allow_ids обновлен\n{allow_ids}')
        except Exception as e:
            logging.critical(e, exc_info=True)


if __name__ == '__main__':
    # asyncio.run(update_allow_ids())
    updating_IDS = threading.Thread(target=update_allow_ids, args=(), daemon=True)
    updating_IDS.start()
    dp.run_polling(bot)
