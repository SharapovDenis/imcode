from io import BytesIO
from requests import get as requests_get
from datetime import datetime
from sys import exc_info
import telebot
import imcode


# read message file
text_messages = imcode.message_file_open("messages/messagefile.txt")
exec(text_messages)

# path to the database book
file_path = imcode.Path.cwd()
database_path = file_path.absolute().joinpath("database/database.xlsx")

# path to the buttons book:
file_path = imcode.Path.cwd()
buttons_path = file_path.absolute().joinpath("database/buttons.xlsx")

# path to the users book:
file_path = imcode.Path.cwd()
users_path = file_path.absolute().joinpath("database/users.xlsx")

# bot initializing
print("Enter TeleBot token, please: ")
token = input()
bot = telebot.TeleBot(token)


@bot.message_handler(commands = ["start", "insert", "show"])
def welcome(message):
    sent_date = datetime.fromtimestamp(message.date)
    
    try:
        chat_id = str(message.chat.id)
        username = message.chat.first_name + " " + message.chat.last_name
        book_data = [chat_id, username]
        
        if imcode.search_row(users_path, chat_id) == -1:
            imcode.buttons_insert(users_path, book_data)
            print(f"New user {chat_id} added to database.")
    
    except RuntimeError:
        print(sent_date, "|", text_messages["ButtonsRunTimeErrorConsole"])
        
    except Exception:
        # error info, type tuple: (class, text, memory position)
        error_text = exc_info()[:2]
        print(sent_date, "|", text_messages["OtherExceptionConsole"], error_text)
    
    to_send = text_messages["ChooseButton"]
      
    keyboard = telebot.types.InlineKeyboardMarkup()
    help_button = telebot.types.InlineKeyboardButton(text="Help", callback_data="help")
    insert_button = telebot.types.InlineKeyboardButton(text="Insert data", callback_data='insert')
    show_button = telebot.types.InlineKeyboardButton(text="Show data", callback_data='show')
    
    keyboard.row(help_button)
    keyboard.row(insert_button, show_button)

    bot.send_message(message.chat.id, to_send, reply_markup=keyboard)
    
    
@bot.message_handler(commands=["help"])
def help_command(message):

    to_send = text_messages["Welcome"]

    bot.send_message(message.chat.id, to_send)
    
    
@bot.message_handler(content_types=["text", "audio", "document", "photo", "sticker", "video"])
def any_text(message):

    to_send = text_messages["AnyMessage"]

    bot.send_message(message.chat.id, to_send) 

    
@bot.callback_query_handler(func=lambda call: True)
def button_answer(call):
    message = call.message
    sent_date = datetime.fromtimestamp(call.message.date)
    identificator = str(message.chat.id)
    
    if call.data == "help":
        
        print(sent_date, "|", "name:", message.chat.first_name, \
                message.chat.last_name, "|", "Help button pressed")
        
        to_send = text_messages["Welcome"]
        
        bot.send_message(call.message.chat.id, to_send)
    
    elif call.data == "insert":
        
        print(sent_date, "|", "name:", message.chat.first_name, \
                message.chat.last_name, "|", "Insert button pressed")
        
        to_send = text_messages["InsertButton"]
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        yes_button = telebot.types.InlineKeyboardButton(text="Yes", callback_data="yes")
        no_button = telebot.types.InlineKeyboardButton(text="No", callback_data="no")
        
        keyboard.row(yes_button, no_button)

        bot.send_message(chat_id=call.message.chat.id, text=to_send, \
                            parse_mode="Markdown", reply_markup=keyboard)
        
    elif call.data == "no":
        
        print(sent_date, "|", "name:", message.chat.first_name, \
                message.chat.last_name, "|", "Insert.No button pressed")
        
        to_send = text_messages["InsertNoButton"]
        
        bot.send_message(chat_id=call.message.chat.id, text=to_send)
        
    elif call.data == "yes":
        
        try:
        
            book_row = imcode.search_row(buttons_path, identificator)
            
            if book_row == -1:
                imcode.buttons_insert(buttons_path, [identificator, False, False])
            
            buttons_data = imcode.buttons_status(buttons_path, identificator)
            
            if buttons_data == None:
                print(sent_date, "|", text_messages["ButtonsNoIdConsole"])
                bot.send_message(message.chat.id, text_messages["ButtonsProblemBot"])
                return

            if buttons_data[1] == True:
                to_send = text_messages["YesAlreadyPressed"]
                bot.send_message(chat_id=call.message.chat.id, text=to_send)
                return
            
            buttons_data[1] = True
            checker = imcode.buttons_change(buttons_path, buttons_data)
            
            if checker == -2:
                print(sent_date, "|", text_messages["ButtonsNotChangedConsole"])
                bot.send_message(message.chat.id, text_messages["ButtonsProblemBot"])
                return
            
        except RuntimeError:
            print(sent_date, "|", text_messages["ButtonsRunTimeErrorConsole"])
            bot.send_message(message.chat.id, text_messages["InsertRuntimeErrorBot"])
            return
        
        except Exception:
            # error info, type tuple: (class, text, memory position)
            error_text = exc_info()[:2]
            print(sent_date, "|", text_messages["OtherExceptionConsole"], error_text)
            bot.send_message(message.chat.id, text_messages["OtherExceptionBot"])
            return
        
        print(sent_date, "|", "name:", message.chat.first_name, \
                message.chat.last_name, "|", "Insert.Yes button pressed")
        
        sent = bot.send_message(message.chat.id, text_messages["InsertYesButton"])
        bot.register_next_step_handler(sent, create_picture)
        
    elif call.data == "show":
        
        try:
            
            book_row = imcode.search_row(buttons_path, identificator)
            
            if book_row == -1:
                imcode.buttons_insert(buttons_path, [identificator, False, False])
            
            buttons_data = imcode.buttons_status(buttons_path, identificator)
            
            if buttons_data == None:
                print(sent_date, "|", text_messages["ButtonsNoIdConsole"])
                bot.send_message(message.chat.id, text_messages["ButtonsProblemBot"])
                return
            
            if buttons_data[2] == True:
                to_send = text_messages["ShowAlreadyPressed"]
                bot.send_message(chat_id=call.message.chat.id, text=to_send)
                return
            
            buttons_data[2] = True
            checker = imcode.buttons_change(buttons_path, buttons_data)
            
            if checker == -2:
                print(sent_date, "|", text_messages["ButtonsNotChangedConsole"])
                bot.send_message(message.chat.id, text_messages["ButtonsProblemBot"])
                return
        
        except RuntimeError:
            print(sent_date, "|", text_messages["ButtonsRunTimeErrorConsole"])
            bot.send_message(message.chat.id, text_messages["InsertRuntimeErrorBot"])
            return
        
        except Exception:
            # error info, type tuple: (class, text, memory position)
            error_text = exc_info()[:2]
            print(sent_date, "|", text_messages["OtherExceptionConsole"], error_text)
            bot.send_message(message.chat.id, text_messages["OtherExceptionBot"])
            return
        
        print(sent_date, "|", "name:", message.chat.first_name, \
                message.chat.last_name, "|", "Show button pressed")
        
        to_send = text_messages["ShowButton"]

        bot.send_message(chat_id=call.message.chat.id, text=to_send, parse_mode="Markdown")
    
        sent = bot.send_message(message.chat.id, text_messages["ShowButtonEnter"])
        bot.register_next_step_handler(sent, create_id)
    

def create_picture(message):

    if not message.text or message.text == None:
        bot.send_message(message.chat.id, text_messages["NoTextBot"])
        return

    data = message.text
    sent_date = datetime.fromtimestamp(message.date)
    identificator = str(message.chat.id)
    
    try:
        image = imcode.data_insert(database_path, data)
        
    except RuntimeError:
        print(sent_date, "|", text_messages["InsertRuntimeErrorConsole"])
        bot.send_message(message.chat.id, text_messages["InsertRuntimeErrorBot"])
        return
    
    except TypeError:
        print(sent_date, "|", text_messages["InsertTypeErrorConsole"])
        bot.send_message(message.chat.id, text_messages["TypeErrorBot"])
        return
    
    except Exception:
        # error info, type tuple: (class, text, memory position)
        error_text = exc_info()[:2]
        print(sent_date, "|", text_messages["OtherExceptionConsole"], error_text)
        bot.send_message(message.chat.id, text_messages["OtherExceptionBot"])
        return
        
    print(sent_date, "|", "name:", message.from_user.first_name, \
            message.from_user.last_name, "|", "text:", message.text)
    
    bot.send_message(message.chat.id, "Saved! Your picture-password:")
    bot.send_photo(message.chat.id, image)
    
    buttons_data = [identificator, False, False]
    imcode.buttons_change(buttons_path, buttons_data)


def create_id(message):
    
    if not message.photo:
        bot.send_message(message.chat.id, text_messages["NoPhotoBot"])
        return
    
    sent_date = datetime.fromtimestamp(message.date)
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    identificator = str(message.chat.id)

    url = "https://api.telegram.org/file/bot" + token + "/" + file_info.file_path

    r = requests_get(url)
    img = imcode.Image.open(BytesIO(r.content))
    
    try:
        data = imcode.show_data(database_path, img)
        
    except TypeError:
        print(sent_date, "|", text_messages["ShowTypeErrorConsole"])
        bot.send_message(message.chat.id, text_messages["TypeErrorBot"])
        return
    
    except ValueError:
        print(sent_date, "|", text_messages["ShowValueErrorConsole"])
        bot.send_message(message.chat.id, text_messages["ShowValueErrorBot"])
        return
    
    except Exception:
        # error info, type tuple: (class, text, memory position)
        error_text = exc_info()[:2]
        print(sent_date, "|", text_messages["OtherExceptionConsole"], error_text)
        bot.send_message(message.chat.id, text_messages["OtherExceptionBot"])
        return
    
    if data == None:
        print(sent_date, "|", text_messages["IdNotFoundConsole"])
        bot.send_message(message.chat.id, text_messages["IdNotFoundBot"])
        return
    
    bot.send_message(message.chat.id, "So good! Your data:")
    bot.send_message(message.chat.id, data)
    
    buttons_data = [identificator, False, False]
    imcode.buttons_change(buttons_path, buttons_data)

bot.polling()

#лучше делать reset при запуске, на случай, если будут
#непредвиденные ошибки

# clear buttons book after turning off the bot
imcode.buttons_reset(buttons_path)
print("\nbuttons book cleared")
