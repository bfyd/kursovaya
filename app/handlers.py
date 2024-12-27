from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from pyexpat.errors import messages

from config import TOKEN
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.types.input_file import FSInputFile

from collections import deque
#.venv\Scripts\activate
import asyncio
import app.keyboards as kb
import config
import random
import os
import regex
import database.requests as rq






router = Router()
bot= Bot(token= TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))


global link
class adm(StatesGroup):
    admin_id = State()
    del_adm = State()
    gen_maze = State()
    get_file = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    if(len(message.text)>=7):
        await rq.new_user(message.text[7:])
        await rq.set_user(message.from_user.id, message.text[7:], message.from_user.is_premium)
    else:
        await rq.set_user(message.from_user.id,None,message.from_user.is_premium)
    await message.answer(f'привет, '+message.from_user.first_name+'!\n\n<b>я бот, который создаёт лабиринты, а также умеет их решать 💔\n\nчтобы узнать на что я способен, жми ниже👇🏻</b>',
                             reply_markup=kb.main)

@router.callback_query(F.data == 'main')
async def main(callback:CallbackQuery,state: FSMContext):
    await callback.message.answer(
        f'привет, ' + callback.from_user.first_name + '!\n\n<b>я бот, который создаёт лабиринты, а также умеет их решать 💔\n\nчтобы узнать на что я способен, жми ниже👇🏻</b>',
        reply_markup=kb.main)

@router.callback_query(F.data == 'create_maze')
async def create_maze(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer('<b>введите размер лабиринта число должно быть не чётным для генерации стен</b>')
    await state.set_state(adm.gen_maze)

@router.message(adm.gen_maze)
async def get_maze_size(message: Message, state:FSMContext):
    text = ''
    try:
            a = 1
            a += int(message.text)
            a-=1
            x = 1/(a%2)
            maze = [['⛔️' for _ in range(a)] for _ in range(a)]
            # Начальная точка
            start_x, start_y = 1, 1
            maze[start_y][start_x] = '⬜️'

            # Стек для хранения пути
            stack = [(start_x, start_y)]

            while stack:
                x, y = stack[-1]

                # Собираем доступные направления
                directions = []
                if x > 1 and maze[y][x - 2] == '⛔️':
                    directions.append((-2, 0))  # Влево
                if x < a - 2 and maze[y][x + 2] == '⛔️':
                    directions.append((2, 0))  # Вправо
                if y > 1 and maze[y - 2][x] == '⛔️':
                    directions.append((0, -2))  # Вверх
                if y < a - 2 and maze[y + 2][x] == '⛔️':
                    directions.append((0, 2))  # Вниз

                if directions:
                    dx, dy = random.choice(directions)
                    maze[y + dy // 2][x + dx // 2] = '⬜️'
                    maze[y + dy][x + dx] = '⬜️'
                    stack.append((x + dx, y + dy))
                else:
                    stack.pop()
            maze[1][1] = '🚀'
            maze[a-2][a-2] = '🏁'
            for row in maze:
                text+=''.join(row)
                text+='\n'
            if (a <= 15):
                with open('data.txt', 'w', encoding='utf-8') as f:
                    f.write(text)
                doc = FSInputFile('data.txt')
                # Отправляем файл пользователю
                with (open('data.txt', 'rb') as f):
                    await message.answer_document(doc)
                await message.answer(f'<code>{text}</code>',reply_markup = await kb.second_part(message.from_user.id))
                await rq.set_maze(message.from_user.id,maze)
            else:
                with open('data.txt', 'w', encoding='utf-8') as f:
                    f.write(text)
                doc = FSInputFile('data.txt')
                # Отправляем файл пользователю
                with (open('data.txt', 'rb') as f):
                    await message.answer_document(doc,reply_markup = await kb.second_part(message.from_user.id))

    except Exception as e:
        print(e)
        await message.answer('ошибка,введите число заново:')
        await state.set_state(adm.gen_maze)

@router.callback_query(lambda callback: callback.data.startswith('play:'))
async def play(callback: CallbackQuery,state: FSMContext):
    msg_id = callback.data.split(':')[1]
    loaded_data = await rq.get_maze(callback.from_user.id)
    loaded_data = loaded_data.split('\n')
    a = len(loaded_data)
    maze = [['' for _ in range(a)] for _ in range(a)]
    a = len(maze[0])
    i=0
    j = 0
    for i in range(len(loaded_data)):
        line = loaded_data[i].split()

        for j in range(len(line)):
            maze[i][j] = line[j]



    print(maze)
    if(a<=15):
        text = ''
        for row in maze:
            text += ''.join(row)
            text += '\n'
        await callback.message.answer(f'<code>{text}</code>',reply_markup = kb.game)
    else:
        await callback.message.answer('слишком большой лабиринт для игры',reply_markup = kb.back)

@router.callback_query(F.data == 'read_maze')
async def read(callback: CallbackQuery,state: FSMContext):
    await callback.message.answer('отправьте файл .txt',reply_markup = kb.back)
    await state.set_state(adm.get_file)

@router.message(adm.get_file,F.document)
async def read(message: Message, state:FSMContext):
    try:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = message.document.file_name

        download_folder = "downloaded_files"
        os.makedirs(download_folder, exist_ok=True)
        local_file_path = os.path.join(download_folder, file_name)

        await bot.download_file(file_path, local_file_path)

        with open(local_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                a = len(line)
                a //= 2

        maze = [['' for _ in range(a)] for _ in range(a)]

        with open(local_file_path, 'r', encoding='utf-8') as file:
            row_index = 0
            for line in file:
                line = line.strip()
                if line and row_index < len(maze):
                    # Разделяем строку на графемовые кластеры
                    symbols = regex.findall(r'\X', line)
                    for col_index, char in enumerate(symbols):
                        if col_index < len(maze[row_index]):
                            maze[row_index][col_index] = char
                    row_index += 1

        start = (1, 1)  # Начальная точка (y, x)
        width, height = len(maze[0]), len(maze)
        goal = (a - 2, a - 2)  # Конечная точка
        queue = deque([start])  # Очередь для BFS
        visited = {start}  # Множество посещённых узлов
        parent = {start: None}  # Словарь для отслеживания пути

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Направления (вперед, вправо, назад, влево)

        while queue:
            current = queue.popleft()

            if current == goal:
                break  # Найдено решение

            for d in directions:
                neighbor = (current[0] + d[0], current[1] + d[1])
                if (0 <= neighbor[0] < height and
                        0 <= neighbor[1] < width and
                        (maze[neighbor[0]][neighbor[1]] == '⬜️' or maze[neighbor[0]][neighbor[1]] == '🚀' or
                         maze[neighbor[0]][neighbor[1]] == '🏁') and
                        neighbor not in visited):
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        # Восстановление пути
        path = []
        step = goal
        print(maze)
        while step is not None:
            path.append(step)
            step = parent[step]

        path.reverse()  # Путь от старта к финишу
        for y, x in path:
            if (not (y == 1 and x == 1) and not (y == a - 2 and x == a - 2)):
                maze[y][x] = '👣'

        text = ''

        for row in maze:
            text += ''.join(row)
            text += '\n'

        if (a <= 15):
            with open('resh.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            doc = FSInputFile('resh.txt')
            # Отправляем файл пользователю
            with (open('resh.txt', 'rb') as f):
                await message.answer_document(doc, caption=f'<code>{text}</code>', reply_markup=kb.back)

            # Удаляем файл после отправки (по желанию)
            os.remove('resh.txt')
        else:
            with open('resh.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            doc = FSInputFile('resh.txt')
            # Отправляем файл пользователю
            with (open('resh.txt', 'rb') as f):
                await message.answer_document(doc, reply_markup=kb.back)

            # Удаляем файл после отправки (по желанию)
            os.remove('resh.txt')

    except Exception as e:
        await message.answer('ошибка попробуйте ещё раз')



@router.callback_query(F.data == 'up')
async def up(callback: CallbackQuery,state: FSMContext):
    await callback.message.delete()
    loaded_data = await rq.get_maze(callback.from_user.id)
    loaded_data = loaded_data.split('\n')
    a = len(loaded_data)
    maze = [['' for _ in range(a)] for _ in range(a)]
    a = len(maze[0])
    i = 0
    j = 0
    for i in range(len(loaded_data)):
        line = loaded_data[i].split()

        for j in range(len(line)):
            maze[i][j] = line[j]
    check = True
    a = len(maze[0])
    for i in range(a):
        for j in range(a):
            if(maze[i][j] == '🚀' and check):
                if(maze[i-1][j] == '⛔️' and check):
                    check = False
                    await callback.message.answer('💥<b>YOU DIED</b>💥',reply_markup = kb.back)
                if (maze[i - 1][j] == '🏁' and check):
                    check = False
                    await callback.message.answer('💥<b>Ура вы финишировали</b>💥', reply_markup=kb.back)
                if (maze[i - 1][j] == '⬜️' and check):
                    check = False
                    msg = await rq.get_game(callback.from_user.id)
                    maze[i][j] = '👣'
                    maze[i-1][j]='🚀'
                    await rq.set_maze(callback.from_user.id, maze)
                    text = ''
                    for row in maze:
                        text += ''.join(row)
                        text += '\n'
                    await callback.message.answer(text = text,reply_markup = kb.game)
                break

@router.callback_query(F.data == 'down')
async def up(callback: CallbackQuery,state: FSMContext):
    await callback.message.delete()
    loaded_data = await rq.get_maze(callback.from_user.id)
    loaded_data = loaded_data.split('\n')
    a = len(loaded_data)
    maze = [['' for _ in range(a)] for _ in range(a)]
    a = len(maze[0])
    i = 0
    j = 0
    for i in range(len(loaded_data)):
        line = loaded_data[i].split()

        for j in range(len(line)):
            maze[i][j] = line[j]

    a = len(maze[0])
    check = True
    for i in range(a):
        for j in range(a):
            if(maze[i][j] == '🚀' and check):
                if(maze[i+1][j] == '⛔️' and check):
                    check = False
                    print(maze[i-1][j])
                    await callback.message.answer('💥<b>YOU DIED</b>💥',reply_markup = kb.back)
                if (maze[i + 1][j] == '🏁' and check):
                    check = False
                    await callback.message.answer('💥<b>Ура вы финишировали</b>💥', reply_markup=kb.back)
                if (maze[i + 1][j] == '⬜️' and check):
                    check = False
                    msg = await rq.get_game(callback.from_user.id)
                    maze[i][j] = '👣'
                    maze[i+1][j]='🚀'
                    await rq.set_maze(callback.from_user.id, maze)
                    text = ''
                    for row in maze:
                        text += ''.join(row)
                        text += '\n'
                    await callback.message.answer(text = text,reply_markup = kb.game)

@router.callback_query(F.data == 'right')
async def up(callback: CallbackQuery,state: FSMContext):
    await callback.message.delete()
    loaded_data = await rq.get_maze(callback.from_user.id)
    loaded_data = loaded_data.split('\n')
    a = len(loaded_data)
    maze = [['' for _ in range(a)] for _ in range(a)]
    a = len(maze[0])
    i = 0
    j = 0
    for i in range(len(loaded_data)):
        line = loaded_data[i].split()

        for j in range(len(line)):
            maze[i][j] = line[j]

    a = len(maze[0])
    check = True
    for i in range(a):
        for j in range(a):
            if(maze[i][j] == '🚀' and check):
                if(maze[i][j+1] == '⛔️' and check):
                    check = False
                    await callback.message.answer('💥<b>YOU DIED</b>💥',reply_markup = kb.back)
                if (maze[i][j + 1] == '🏁' and check):
                    check = False
                    await callback.message.answer('💥<b>Ура вы финишировали</b>💥', reply_markup=kb.back)
                if (maze[i][j + 1] == '⬜️' and check):
                    check = False
                    msg = await rq.get_game(callback.from_user.id)
                    maze[i][j] = '👣'
                    maze[i][j+1]='🚀'
                    await rq.set_maze(callback.from_user.id, maze)
                    text = ''
                    for row in maze:
                        text += ''.join(row)
                        text += '\n'
                    await callback.message.answer(text = text,reply_markup = kb.game)
                break

@router.callback_query(F.data == 'left')
async def up(callback: CallbackQuery,state: FSMContext):
    await callback.message.delete()
    loaded_data = await rq.get_maze(callback.from_user.id)
    loaded_data = loaded_data.split('\n')
    a = len(loaded_data)
    maze = [['' for _ in range(a)] for _ in range(a)]
    a = len(maze[0])
    i = 0
    j = 0
    for i in range(len(loaded_data)):
        line = loaded_data[i].split()

        for j in range(len(line)):
            maze[i][j] = line[j]

    a = len(maze[0])
    check = True
    for i in range(a):
        for j in range(a):
            if(maze[i][j] == '🚀' and check):
                if(maze[i][j-1] == '⛔️' and check):
                    check = False
                    await callback.message.answer('💥<b>YOU DIED</b>💥',reply_markup = kb.back)
                if (maze[i][j - 1] == '🏁' and check):
                    check = False
                    await callback.message.answer('💥<b>Ура вы финишировали</b>💥', reply_markup=kb.back)
                if (maze[i][j - 1] == '⬜️' and check):
                    check = False
                    msg = await rq.get_game(callback.from_user.id)
                    maze[i][j] = '👣'
                    maze[i][j-1]='🚀'
                    await rq.set_maze(callback.from_user.id, maze)
                    text = ''
                    for row in maze:
                        text += ''.join(row)
                        text += '\n'
                    await callback.message.answer(text = text,reply_markup = kb.game)
                break

@router.callback_query(F.data == 'create_resh')
async def create_resh(callback: CallbackQuery,state: FSMContext):

            try:

                with open('data.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        a = len(line)
                        a//=2


                maze = [['' for _ in range(a)] for _ in range(a)]


                with open('data.txt', 'r', encoding='utf-8') as file:
                    row_index = 0
                    for line in file:
                        line = line.strip()
                        if line and row_index < len(maze):
                            # Разделяем строку на графемовые кластеры
                            symbols = regex.findall(r'\X', line)
                            for col_index, char in enumerate(symbols):
                                if col_index < len(maze[row_index]):
                                    maze[row_index][col_index] = char
                            row_index += 1


                start = (1, 1)  # Начальная точка (y, x)
                width, height = len(maze[0]), len(maze)
                goal = (a - 2, a - 2)  # Конечная точка
                queue = deque([start])  # Очередь для BFS
                visited = {start}  # Множество посещённых узлов
                parent = {start: None}  # Словарь для отслеживания пути

                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Направления (вперед, вправо, назад, влево)

                while queue:
                    current = queue.popleft()

                    if current == goal:
                        break  # Найдено решение

                    for d in directions:
                        neighbor = (current[0] + d[0], current[1] + d[1])
                        if (0 <= neighbor[0] < height and
                                0 <= neighbor[1] < width and
                                (maze[neighbor[0]][neighbor[1]] == '⬜️' or maze[neighbor[0]][neighbor[1]] == '🚀' or maze[neighbor[0]][neighbor[1]] == '🏁' )and
                                neighbor not in visited):
                            visited.add(neighbor)
                            parent[neighbor] = current
                            queue.append(neighbor)

                # Восстановление пути
                path = []
                step = goal
                print(maze)
                while step is not None:
                    path.append(step)
                    step = parent[step]

                path.reverse()  # Путь от старта к финишу
                for y, x in path:
                    if(not(y == 1 and x == 1) and not(y == a-2 and x == a-2)):
                        maze[y][x] = '👣'

                text = ''

                for row in maze:
                    text += ''.join(row)
                    text += '\n'

                if (a <= 15):
                    with open('resh.txt', 'w', encoding='utf-8') as f:
                        f.write(text)
                    doc = FSInputFile('resh.txt')
                    # Отправляем файл пользователю
                    with (open('resh.txt', 'rb') as f):
                        await callback.message.answer_document(doc,caption = f'<code>{text}</code>',reply_markup = kb.back)

                    # Удаляем файл после отправки (по желанию)
                    os.remove('resh.txt')
                else:
                    with open('resh.txt', 'w', encoding='utf-8') as f:
                        f.write(text)
                    doc = FSInputFile('resh.txt')
                    # Отправляем файл пользователю
                    with (open('resh.txt', 'rb') as f):
                        await callback.message.answer_document(doc,reply_markup = kb.back)

                    # Удаляем файл после отправки (по желанию)
                    os.remove('resh.txt')

            except Exception as e:
                pass

