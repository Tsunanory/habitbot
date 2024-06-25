import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

import requests
from django.conf import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

REGISTER_USERNAME, REGISTER_PASSWORD, LOGIN_USERNAME, LOGIN_PASSWORD, CREATE_ACTION, CREATE_TIME, CREATE_PLACE, EDIT_HABIT_ID, EDIT_ACTION, EDIT_TIME, EDIT_PLACE, DELETE_HABIT_ID = range(12)


async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please enter your username to register:')
    return REGISTER_USERNAME


async def register_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['register_username'] = update.message.text
    await update.message.reply_text('Please enter your password:')
    return REGISTER_PASSWORD


async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data['register_username']
    password = update.message.text
    response = requests.post(f'{settings.BACKEND_URL}/api/register/', data={
        'username': username,
        'password': password
    })
    if response.status_code == 200:
        tokens = response.json()
        if 'access' in tokens and 'refresh' in tokens:
            context.user_data['access_token'] = tokens['access']
            context.user_data['refresh_token'] = tokens['refresh']
            await update.message.reply_text('Registration successful! You are now logged in.')
        else:
            logger.error(f"Unexpected response format: {tokens}")
            await update.message.reply_text('Registration failed. Unexpected response format. Please try again later.')
    else:
        await update.message.reply_text('Registration failed. Try again.')
    return ConversationHandler.END


async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please enter your username to log in:')
    return LOGIN_USERNAME


async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['login_username'] = update.message.text
    await update.message.reply_text('Please enter your password:')
    return LOGIN_PASSWORD


async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data['login_username']
    password = update.message.text
    response = requests.post(f'{settings.BACKEND_URL}/api/login/', data={
        'username': username,
        'password': password
    })
    if response.status_code == 200:
        tokens = response.json()
        context.user_data['access_token'] = tokens['access']
        context.user_data['refresh_token'] = tokens['refresh']
        await update.message.reply_text('Login successful!')
    else:
        await update.message.reply_text('Login failed. Try again.')
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'access_token' in context.user_data:
        await update.message.reply_text(
            '/list - list of your habits\n'
            '/pub_list - list of public habits\n'
            '/create - create new habit\n'
            '/edit - edit habit\n'
            '/delete - delete habit'
        )
    else:
        await update.message.reply_text('Use /register to sign up or /login to log in.')


async def list_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'access_token' not in context.user_data:
        await update.message.reply_text('Please log in first using /login.')
        return

    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    response = requests.get(f'{settings.BACKEND_URL}/api/habits/', headers=headers)
    if response.status_code == 200:
        habits = response.json()
        if not habits:
            await update.message.reply_text('You don\'t have any habits yet.')
        else:
            habit_list = '\n'.join([f'{habit["action"]} at {habit["time"]} in {habit["place"]}' for habit in habits])
            await update.message.reply_text(f'Your habits:\n{habit_list}')
    else:
        await update.message.reply_text('Failed to retrieve habits.')


async def list_public_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = requests.get(f'{settings.BACKEND_URL}/api/habits/public/')
    if response.status_code == 200:
        habits = response.json()
        logger.info(f'Public habits response: {habits}')  # Log the response to debug

        # Check if the 'results' key is present and is a list
        if 'results' in habits and isinstance(habits['results'], list):
            if not habits['results']:
                await update.message.reply_text('No public habits available.')
            else:
                habit_list = '\n'.join([f'{habit["action"]} at {habit["time"]} in {habit["place"]}' for habit in habits['results']])
                await update.message.reply_text(f'Public habits:\n{habit_list}')
        else:
            await update.message.reply_text('Failed to retrieve public habits. Invalid response format.')
    else:
        await update.message.reply_text('Failed to retrieve public habits.')


async def create_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Enter the action for the new habit:')
    return CREATE_ACTION


async def save_habit_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_action'] = update.message.text
    await update.message.reply_text('Enter the time for the new habit:')
    return CREATE_TIME


async def save_habit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_time'] = update.message.text
    await update.message.reply_text('Enter the place for the new habit:')
    return CREATE_PLACE


async def save_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    action = context.user_data['habit_action']
    time = context.user_data['habit_time']
    place = update.message.text
    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    response = requests.post(f'{settings.BACKEND_URL}/api/habits/', headers=headers, data={
        'action': action,
        'time': time,
        'place': place,
        'is_public': False  # or True, depending on your requirements
    })
    if response.status_code == 201:
        await update.message.reply_text('Habit created successfully!')
    else:
        await update.message.reply_text('Failed to create habit. Try again.')
    return ConversationHandler.END


async def start_edit_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Enter the ID of the habit you want to edit:')
    return EDIT_HABIT_ID


async def edit_habit_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_id'] = update.message.text
    await update.message.reply_text('Enter the new action for the habit:')
    return EDIT_ACTION


async def edit_habit_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_action'] = update.message.text
    await update.message.reply_text('Enter the new time for the habit:')
    return EDIT_TIME


async def edit_habit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_time'] = update.message.text
    await update.message.reply_text('Enter the new place for the habit:')
    return EDIT_PLACE


async def save_edited_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    habit_id = context.user_data['habit_id']
    action = context.user_data['habit_action']
    time = context.user_data['habit_time']
    place = update.message.text
    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    response = requests.put(f'{settings.BACKEND_URL}/api/habits/{habit_id}/', headers=headers, data={
        'action': action,
        'time': time,
        'place': place
    })
    if response.status_code == 200:
        await update.message.reply_text('Habit updated successfully!')
    else:
        await update.message.reply_text('Failed to update habit. Try again.')
    return ConversationHandler.END


async def start_delete_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Enter the ID of the habit you want to delete:')
    return DELETE_HABIT_ID


async def delete_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    habit_id = update.message.text
    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    response = requests.delete(f'{settings.BACKEND_URL}/api/habits/{habit_id}/', headers=headers)
    if response.status_code == 204:
        await update.message.reply_text('Habit deleted successfully!')
    else:
        await update.message.reply_text('Failed to delete habit. Try again.')
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Use /register to sign up or /login to log in.')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    register_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', start_register)],
        states={
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    login_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', start_login)],
        states={
            LOGIN_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
            LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    create_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_habit)],
        states={
            CREATE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_action)],
            CREATE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_time)],
            CREATE_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    edit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('edit', start_edit_habit)],
        states={
            EDIT_HABIT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_id)],
            EDIT_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_action)],
            EDIT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_time)],
            EDIT_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_habit)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', start_delete_habit)],
        states={
            DELETE_HABIT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_habit)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(register_conv_handler)
    application.add_handler(login_conv_handler)
    application.add_handler(create_conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(delete_conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_habits))
    application.add_handler(CommandHandler("pub_list", list_public_habits))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()
