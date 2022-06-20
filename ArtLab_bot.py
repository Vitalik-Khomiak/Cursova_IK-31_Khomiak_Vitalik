#PART 1 'import'
import logging   #імпорт бібліотеки loggining 
import privat24   #імпорт бібліотеки privat24
# імпорт бібліотеки Aiogram - зовнішня бібліотека для роботи з API telegram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
from test import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
import sqlite3   # Імпорт бібліотеки для роботи з базою даних



API_TOKEN = '5193710230:AAHx5x0Ek1uK6vY9eDk6EZrrbmgG9z9rJTc'   #токен бота
logging.basicConfig(level=logging.INFO)   #налаштування logging
bot = Bot(token=API_TOKEN)   #ініціалізація бота
storage = MemoryStorage()   #ініціалізація змінної для зберігання states в пам'ять
dp = Dispatcher(bot,storage=storage)   #ініціалізація dispatcher


con = sqlite3.connect('user.db')   #підключення бази даних
cur = con.cursor()   #створюємо курсор


#Створюємо клас із states для покрокового виконання команд
class ArtLabState(StatesGroup):
    Username = State()
    Del = State()
    Compare_first = State()
    Compare_second = State()
    stat=State()


# Декоратор обробника буде викликаний, якщо повідомлення починається з команди "/ start" і запускає функцію "start_command"
@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    await ArtLabState.Username.set()   #перехід на наступний state Username
    await message.answer(   # вивід інформації повідомленням в телеграм боті
        fmt.text(   
            fmt.text(fmt.hbold('How to name data...')),   #кастомізація повідомлення
            sep='/n'
        ), parse_mode="HTML"
    ) 


# Декоратор обробника буде викликаний, якщо повідомлення починається з команди "/ stat" і запускає функцію "start_command"
@dp.message_handler(commands="compare")
async def start_command(message: types.Message):
    cur.execute('SELECT * FROM data WHERE UserId = ?', (message.from_user.id, ))
    search=cur.fetchall()   #Збір  даних з бази даних
    if len(search) != 0:   #перевіряє, чи правильно введено назва даних
        await ArtLabState.Compare_first.set()   #перехід на наступний state Compare_first
        cur.execute("SELECT Username FROM data")   #перевіряє, чи правильно введено назва даних
        compare=cur.fetchall()   #Збір  даних з бази даних
        for i in compare:
            i = i[0]
            await message.answer(i)   # вивід інформації повідомленням в телеграм боті
        await message.answer(
                fmt.text(   
                    fmt.text(fmt.hbold('Type first data:')),   #кастомізація повідомлення
                    sep='/n'
                ), parse_mode="HTML"
            ) 
    else:
        await message.answer(   #вивід інформації повідомленням в телеграм боті
            fmt.text(   
                fmt.text(fmt.hbold('Data list is EMPTY')),   #кастомізація повідомлення
                sep='/n'
            ), parse_mode="HTML"
        ) 


# Декоратор обробника буде викликаний, якщо повідомлення починається з команди "/ cancel" і запускає функцію "start_command"
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()   #зупинка state
    await message.reply('Cancelled, enter another command', reply_markup=types.ReplyKeyboardRemove())


# Декоратор обробника буде викликаний, якщо повідомлення починається з команди "/ help" і запускає функцію "start_command"
@dp.message_handler(commands="help")
async def start_command(message: types.Message):
    await message.answer(   #вивід інформації повідомленням в телеграм боті
        fmt.text( 
            fmt.text(fmt.hbold('Your commands:')),   #кастомізація повідомлення
            sep='/n' 
        ), parse_mode="HTML"
    ) 
    await message.answer('/help\n/start\n/cancel\n/delete_data\n/stat\n/compare')   #вивід інформації повідомленням в телеграм боті




#Декоратор для обробника стану, який перевіряє чи база даних має записи і, якщо вони є виводить список
@dp.message_handler(commands="delete_data")
async def start_command(message: types.Message, state: FSMContext):
    await ArtLabState.Del.set()  #перехід на наступний state Del
    global search
    cur.execute('SELECT * FROM data WHERE UserId = ?', (message.from_user.id, ))   #пошук 
    search=cur.fetchall()   #Збір даних з бази даних

    
    if len(search) != 0:
        await message.answer(   #вивід інформації повідомленням в телеграм боті
            fmt.text( 
                fmt.text(fmt.hbold('Data list:')),   #кастомізація повідомлення
                sep='/n'
            ), parse_mode="HTML"
        ) 


        for i in range(len(search)):
            print(search[i][1])
            await message.answer(   #вивід інформації повідомленням в телеграм боті
            fmt.text( 
                fmt.text(fmt.hitalic(search[i][1])),   #кастомізація повідомлення
                sep='/n'
            ), parse_mode="HTML"
        ) 

        await message.answer(   #вивід інформації повідомленням в телеграм боті
            fmt.text( 
                fmt.text(fmt.hbold('Type del name...')),   #кастомізація повідомлення
                sep='/n'
            ), parse_mode="HTML"
        ) 
    else:
        await state.finish()   #зупинка state
        await message.answer(   #вивід інформації повідомленням в телеграм боті
            fmt.text(   
                fmt.text(fmt.hbold('Data list is EMPTY')),   #кастомізація повідомлення
                sep='/n'
            ), parse_mode="HTML"
        ) 


#Декоратор для обробника стану, який перевіряє чи введена користувачем назва є в базі даних
@dp.message_handler(state=ArtLabState.Del)
async def echo(message: types.Message, state: FSMContext):
    await state.finish()   #зупинка state
    del_name=message.text   #присвоюємо змінній текст введений користувачем
    cur.execute('SELECT * FROM data WHERE Username = ?', (del_name, ))
    delsearch=cur.fetchall()   #Збір  даних з бази даних
    if len(delsearch) != 0:
        cur.execute('DELETE FROM data WHERE Username=?', (del_name,))
        con.commit()   # Комміт дій до бази даних
        del_name=f'{del_name} was deleted'
        await message.answer(del_name)   #вивід інформації повідомленням в телеграм боті
        
    else:
        await message.answer('Incorrect name')   #вивід інформації повідомленням в телеграм боті

#Декоратор для обробника стану, який перевіряє чи Username записаний в базі даних
@dp.message_handler(state=ArtLabState.Username)
async def echo(message: types.Message, state: FSMContext):
  
    global Username   #робимо змунну Username глобальною
    Username = message.text   #присвоюємо змінній текст введений користувачем
    cur.execute('SELECT * FROM data WHERE Username = ?', (Username, ))
    _data=cur.fetchall()   #Збір  даних з бази даних 
    

    if len(_data)==0:    # якщо нуль(тобто userid немає)
        await state.finish()   #зупинка state
        await message.reply("Data name: "+Username)
        print('There is no component named %s'%Username)
        await bot.send_message(message.chat.id,"Please select a date range : ", reply_markup=await DialogCalendar().start_calendar())
    else:        # якщо юзер ід є
        await ArtLabState.Username.set()   #перехід на наступний state Username
        print('Component %s found with rowids %s'%(Username,','.join(map(str, next(zip(*_data))))))
        print(_data[0])
        await message.answer(   #вивід інформації повідомленням в телеграм боті
        fmt.text( 
            fmt.text(fmt.hbold('Yo are already in database')),   #кастомізація повідомлення
            sep='/n'
        ), parse_mode="HTML"
    ) 
        await message.answer(   #вивід інформації повідомленням в телеграм боті
        fmt.text( 
            fmt.text(fmt.hbold('Please enter another name :')),   #кастомізація повідомлення
            sep='/n'
        ), parse_mode="HTML"
    ) 



#Декоратор для обробника стану,який перевіряє чи існує в базі даних назва введена юзером
@dp.message_handler(state=ArtLabState.Compare_first)
async def echo(message: types.Message, state: FSMContext):
    global first_data
    first_data=message.text   #присвоюємо змінній текст введений користувачем
    cur.execute('SELECT * FROM data WHERE Username = ?', (first_data, ))
    delsearch1=cur.fetchall()   #Збір  даних з бази даних
    if len(delsearch1) != 0:
        await message.answer(   #вивід інформації повідомленням в телеграм боті
                fmt.text( 
                    fmt.text(fmt.hbold('Type Second data:')),   #кастомізація повідомлення
                    sep='/n'
                ), parse_mode="HTML"
            ) 
        await ArtLabState.Compare_second.set()  #перехід на наступний state Compare_second

    else:
        await message.answer('Incorect name')   #вивід інформації повідомленням в телеграм боті

#Декоратор для обробника стану,який порівнює два масиви даних     
@dp.message_handler(state=ArtLabState.Compare_second)
async def echo(message: types.Message, state: FSMContext):
    second_data=message.text   #присвоюємо змінній текст введений користувачем
    cur.execute('SELECT * FROM data WHERE Username = ?', (second_data, ))
    delsearch1=cur.fetchall()   #Збір  даних з бази даних
    if len(delsearch1) != 0:

        cur.execute("SELECT * FROM data WHERE Username=?",(first_data,))
        first_data_arr=cur.fetchall()   #Збір  даних з бази даних

        cur.execute("SELECT * FROM data WHERE Username=?",(second_data,))
        second_data_arr=cur.fetchall()   #Збір  даних з бази даних

        await message.answer(first_data_arr[0][1])   #вивід інформації повідомленням в телеграм боті
        await message.answer(second_data_arr[0][1])   #вивід інформації повідомленням в телеграм боті

        general_title="Compare Predict"
        a1_titel=f"{first_data_arr[0][1]}"
        a2_titel=f"{second_data_arr[0][1]}"
        privat24.PrintMatplotlib(float(first_data_arr[0][2]),float(second_data_arr[0][2]),general_title,a1_titel,a2_titel)

        await message.answer_photo(   #вивід фото повідомленням в телеграм боті
                open(r'D:\OneDrive\Документи\University\Cursova\v2\tmp\grath.png', 'rb'),
                reply_markup = None
            )

        general_title="Compare Income"
        a1_titel=f"{first_data_arr[0][1]}"
        a2_titel=f"{second_data_arr[0][1]}"
        privat24.PrintMatplotlib(float(first_data_arr[0][3]),float(second_data_arr[0][3]),general_title,a1_titel,a2_titel)

        await message.answer_photo(   #вивід фото повідомленням в телеграм боті
                open(r'D:\OneDrive\Документи\University\Cursova\v2\tmp\grath.png', 'rb'),
                reply_markup = None
            )

        general_title="Compare Outcome"
        a1_titel=f"{first_data_arr[0][1]}"
        a2_titel=f"{second_data_arr[0][1]}"
        privat24.PrintMatplotlib(float(first_data_arr[0][4]),float(second_data_arr[0][4]),general_title,a1_titel,a2_titel)

        await message.answer_photo(   #вивід фото повідомленням в телеграм боті
                open(r'D:\OneDrive\Документи\University\Cursova\v2\tmp\grath.png', 'rb'),
                reply_markup = None
            )
        await state.finish()   #зупинка state
    else:
        await message.answer('Incorect name')   #вивід інформації повідомленням в телеграм боті
        


#ініціалізація змінних
start_date = ''
end_date = ''
msa=0


#Дозволяє користувачу ввести першу дату
@dp.callback_query_handler(dialog_cal_callback.filter())
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    global start_date
    if selected:
        start_date = date.strftime("%d.%m.%Y")
        await callback_query.message.answer(   #вивід start_date повідомленням в телеграм боті
            start_date,
            reply_markup=await SimpleCalendar().start_calendar()
        )

#Дозволяє користувачу ввести другу дату і здійснює звернення до privat24.py для обрахунків
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict):
    
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    global msa
    if selected:
        end_date = date.strftime("%d.%m.%Y")   #запис кінцевої дати в змінну
        await callback_query.message.answer(   #вивід end_date повідомленням в телеграм боті
            end_date,
            reply_markup=await SimpleCalendar().start_calendar()
        )
        pr_arr,predict,plus,minus = privat24.privat_bank(start_date,end_date) # зверненняя до функції privat_bank з файлу privat24.py(і запис результату в чотири змінні (pr_arr,predict,plus,minus))
        predict=round(predict)  #округлення передбачення
        msa = ''
        for i in pr_arr:
            msa = msa+i+"\n"
        user_id=callback_query.message.chat.id  #отримання userid
        cur.execute(f"INSERT INTO data VALUES ({user_id}, '{Username}', '{predict}','{plus}','{minus}','{start_date}','{end_date}')")   #записа даних в базу даних
        con.commit()   # Комміт дій до бази даних
        
        await callback_query.message.answer_photo(   #вивід фото повідомленням в телеграм боті
            open(r'D:\OneDrive\Документи\University\Cursova\v2\tmp\grath.png', 'rb'),
            reply_markup = None
        )
        predict = f'Predict :  {predict}'
        await callback_query.message.answer(   #вивід передбачення повідомленням в телеграм боті
            predict
        )
        await callback_query.message.answer("If you want transactions details \nStart:  /stat")   #вивід інформації повідомленням в телеграм боті
        

# Декоратор обробника буде викликаний, якщо повідомлення починається з команди "/ stat" і запускає функцію "start_command"
@dp.message_handler(commands="stat")
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()   #зупинка state
    if msa!=0:
        await message.answer(msa)   #вивід інформації повідомленням в телеграм боті
    else:
        await message.answer(   #вивід інформації повідомленням в телеграм боті
                fmt.text( 
                    fmt.text(fmt.hbold('Please enter data first\nPress: /start')),   #кастомізація повідомлення
                    
                    sep='/n'
                ), parse_mode="HTML"
            ) 



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)






