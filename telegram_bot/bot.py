import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
import requests
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

REGISTER_USERNAME, REGISTER_PASSWORD, LOGIN_USERNAME, LOGIN_PASSWORD = range(4)
CREATE_IS_PLEASANT, CREATE_ACTION, CREATE_TIME, CREATE_PLACE, CREATE_BOUND, CREATE_PUBLIC, CHOOSE_OR_CREATE_PLEASANT_HABIT = range(4, 11)
EDIT_HABIT_ID, EDIT_ACTION, EDIT_TIME, EDIT_PLACE = range(11, 15)
DELETE_HABIT_ID = 15
LIST_PAGINATION = range(100, 101)
PUB_LIST_PAGINATION = range(101, 102)


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


async def start_list_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'access_token' not in context.user_data:
        await update.message.reply_text('Please log in first using /login.')
        return ConversationHandler.END

    return await list_habits(update, context, page=1)


async def list_habits(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1) -> int:
    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    response = requests.get(f'{settings.BACKEND_URL}/api/habits/?page={page}', headers=headers)
    if response.status_code == 200:
        habits = response.json()
        logger.info(f'Habits response: {habits}')  # Log the response to debug

        if 'results' in habits and isinstance(habits['results'], list):  # Ensure habits is a list
            if not habits['results']:
                await update.message.reply_text('Your list of habits is empty.')
                return ConversationHandler.END
            else:
                habit_list = []
                for habit in habits['results']:
                    habit_info = f'{habit["id"]}: {habit["action"]} at {habit["time"]} in {habit["place"]}'
                    if habit['related_habit']:
                        related_habit = habit['related_habit']
                        habit_info += f' related: {related_habit["id"]}: {related_habit["action"]} at {related_habit["time"]} in {related_habit["place"]}'
                    habit_list.append(habit_info)

                total_pages = habits['count'] // 5 + (1 if habits['count'] % 5 > 0 else 0)
                current_page = page
                message = '\n'.join(habit_list)
                message += f'\n\nPage {current_page} of {total_pages}\nEnter the number of page or "quit" to leave list.'

                await update.message.reply_text(message)
                context.user_data['total_pages'] = total_pages
                context.user_data['current_page'] = current_page
                return LIST_PAGINATION
        else:
            await update.message.reply_text('Failed to retrieve habits. Invalid response format.')
            return ConversationHandler.END
    else:
        await update.message.reply_text('Failed to retrieve habits.')
        return ConversationHandler.END


async def paginate_list_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip().lower()
    if user_input == 'quit':
        await update.message.reply_text(
            '/list - list of your habits\n'
            '/pub_list - list of public habits\n'
            '/create - create new habit\n'
            '/edit - edit habit\n'
            '/delete - delete habit'
        )
        return ConversationHandler.END
    else:
        try:
            page = int(user_input)
            if 1 <= page <= context.user_data['total_pages']:
                return await list_habits(update, context, page=page)
            else:
                await update.message.reply_text(
                    'Invalid page number. Please enter a valid page number or "quit" to leave list.')
                return LIST_PAGINATION
        except ValueError:
            await update.message.reply_text('Invalid input. Please enter a valid page number or "quit" to leave list.')
            return LIST_PAGINATION


async def start_list_public_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await list_public_habits(update, context, page=1)


async def list_public_habits(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1) -> int:
    response = requests.get(f'{settings.BACKEND_URL}/api/habits/public/?page={page}')
    if response.status_code == 200:
        habits = response.json()
        logger.info(f'Public habits response: {habits}')  # Log the response to debug

        if 'results' in habits and isinstance(habits['results'], list):  # Ensure habits is a list
            if not habits['results']:
                await update.message.reply_text('No public habits available.')
                return ConversationHandler.END
            else:
                habit_list = []
                for habit in habits['results']:
                    habit_info = f'{habit["id"]}: {habit["action"]} at {habit["time"]} in {habit["place"]}'
                    if habit['related_habit']:
                        related_habit = habit['related_habit']
                        habit_info += f' related: {related_habit["id"]}: {related_habit["action"]} at {related_habit["time"]} in {related_habit["place"]}'
                    habit_list.append(habit_info)

                total_pages = habits['count'] // 5 + (1 if habits['count'] % 5 > 0 else 0)
                current_page = page
                message = '\n'.join(habit_list)
                message += f'\n\nPage {current_page} of {total_pages}\nEnter the number of page or "quit" to leave list.'

                await update.message.reply_text(message)
                context.user_data['total_pages'] = total_pages
                context.user_data['current_page'] = current_page
                return PUB_LIST_PAGINATION
        else:
            await update.message.reply_text('Failed to retrieve public habits. Invalid response format.')
            return ConversationHandler.END
    else:
        await update.message.reply_text('Failed to retrieve public habits.')
        return ConversationHandler.END


async def paginate_list_public_habits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip().lower()
    if user_input == 'quit':
        await update.message.reply_text(
            '/list - list of your habits\n'
            '/pub_list - list of public habits\n'
            '/create - create new habit\n'
            '/edit - edit habit\n'
            '/delete - delete habit'
        )
        return ConversationHandler.END
    else:
        try:
            page = int(user_input)
            if 1 <= page <= context.user_data['total_pages']:
                return await list_public_habits(update, context, page=page)
            else:
                await update.message.reply_text(
                    'Invalid page number. Please enter a valid page number or "quit" to leave list.')
                return PUB_LIST_PAGINATION
        except ValueError:
            await update.message.reply_text('Invalid input. Please enter a valid page number or "quit" to leave list.')
            return PUB_LIST_PAGINATION

async def create_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Are you creating a pleasant habit? (yes/no)')
    return CREATE_IS_PLEASANT

async def save_habit_is_pleasant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = update.message.text.lower()
    while response not in ['yes', 'no']:
        await update.message.reply_text('Please answer "yes" or "no". Are you creating a pleasant habit?')
        response = (await context.bot.get_chat(update.effective_chat.id)).text.lower()
    context.user_data['is_pleasant'] = (response == 'yes')
    await update.message.reply_text('Do you want this habit to be public? (yes/no)')
    return CREATE_PUBLIC


async def save_habit_is_public(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = update.message.text.lower()
    while response not in ['yes', 'no']:
        await update.message.reply_text('Please answer "yes" or "no". Do you want this habit to be public?')
        response = (await context.bot.get_chat(update.effective_chat.id)).text.lower()
    context.user_data['is_public'] = (response == 'yes')

    if context.user_data['is_pleasant']:
        await update.message.reply_text('Enter the action for the new habit:')
        return CREATE_ACTION
    else:
        await update.message.reply_text('Enter the action for the new habit:')
        return CREATE_ACTION


async def save_habit_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_action'] = update.message.text
    await update.message.reply_text('Enter the time for the new habit (HH:MM):')
    return CREATE_TIME

async def save_habit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['habit_time'] = update.message.text
    await update.message.reply_text('Enter the place for the new habit:')
    return CREATE_PLACE


async def save_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    action = context.user_data['habit_action']
    time = context.user_data['habit_time']
    place = update.message.text
    is_pleasant = context.user_data.get('is_pleasant', False)
    is_public = context.user_data.get('is_public', False)
    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    payload = {
        'action': action,
        'time': time,
        'place': place,
        'is_public': is_public,
        'duration': 60,
        'frequency': 1,
        'is_pleasant': is_pleasant
    }

    try:
        response = requests.post(f'{settings.BACKEND_URL}/api/habits/', headers=headers, data=payload)
        logger.info(f'Create habit response: {response.status_code}, {response.text}')
        if response.status_code == 201:
            new_habit = response.json()
            context.user_data['new_habit_id'] = new_habit['id']
            logger.info(f'New habit created with ID: {new_habit["id"]}')
            if is_pleasant:
                await update.message.reply_text('Habit created successfully!')
                return ConversationHandler.END
            else:
                await update.message.reply_text('Do you want to bind another habit to this one? (yes/no)')
                return CREATE_BOUND
        else:
            await update.message.reply_text(f'Failed to create habit. {response.text}')
            return ConversationHandler.END
    except Exception as e:
        logger.error(f'Error occurred during habit creation: {str(e)}')
        await update.message.reply_text('Failed to create habit due to an unexpected error.')
        return ConversationHandler.END


async def bind_pleasant_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = update.message.text.lower()
    logger.info(f'User response to bind another habit: {response}')
    if response not in ['yes', 'no']:
        await update.message.reply_text('Please answer "yes" or "no". Do you want to bind another habit to this one?')
        return CREATE_BOUND

    if response == 'no':
        await update.message.reply_text('Habit created successfully!')
        return ConversationHandler.END

    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    response = requests.get(f'{settings.BACKEND_URL}/api/habits/', headers=headers, params={'is_pleasant': 'true', 'no_pagination': 'true'})
    if response.status_code == 200:
        habits = response.json()
        logger.info(f'Retrieved pleasant habits for binding: {habits}')
        if isinstance(habits, list):
            if not habits:
                await update.message.reply_text('You don\'t have any pleasant habits to bind.')
                return ConversationHandler.END
            else:
                habit_list = '\n'.join([f'{habit["id"]}: {habit["action"]} at {habit["time"]} in {habit["place"]}' for habit in habits])
                await update.message.reply_text(f'Pleasant habits:\n{habit_list}\nChoose ID of habit to bind with or create new habit (insert ID or "create")')
                return CHOOSE_OR_CREATE_PLEASANT_HABIT
        else:
            await update.message.reply_text('Failed to retrieve habits. Invalid response format.')
            return ConversationHandler.END
    else:
        await update.message.reply_text('Failed to retrieve habits.')
        return ConversationHandler.END


async def choose_or_create_pleasant_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.lower()
    logger.info(f'User choice for binding habit: {choice}')
    if choice == 'create':
        await update.message.reply_text('Enter the action for the new habit:')
        return CREATE_ACTION

    try:
        habit_id = int(choice)
        logger.info(f'Chosen habit ID to bind: {habit_id}')
        headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
        new_habit_id = context.user_data['new_habit_id']
        logger.info(f'Updating new habit ID: {new_habit_id} with related habit ID: {habit_id}')
        update_payload = {'related_habit': habit_id}
        response = requests.patch(f'{settings.BACKEND_URL}/api/habits/{new_habit_id}/', headers=headers, json=update_payload)
        logger.info(f'Update habit response: {response.status_code}, {response.text}')
        if response.status_code == 200:
            await update.message.reply_text('Habit created and bound successfully!')
        else:
            await update.message.reply_text(f'Failed to bind habit. {response.text}')
            logger.error(f'Failed to bind habit: {response.status_code}, {response.text}')
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text('Invalid input. Please enter a valid habit ID or "create".')
        return CHOOSE_OR_CREATE_PLEASANT_HABIT
    except Exception as e:
        logger.error(f'Error occurred during habit binding: {str(e)}')
        await update.message.reply_text('Failed to bind habit due to an unexpected error.')
        return ConversationHandler.END


async def start_edit_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Enter the ID of the habit you want to edit or type "quit" to cancel:')
    return EDIT_HABIT_ID

async def edit_habit_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == 'quit':
        await update.message.reply_text('Edit operation cancelled.')
        return ConversationHandler.END
    context.user_data['habit_id'] = update.message.text
    await update.message.reply_text('Enter the new action for the habit or type "quit" to cancel:')
    return EDIT_ACTION

async def edit_habit_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == 'quit':
        await update.message.reply_text('Edit operation cancelled.')
        return ConversationHandler.END
    context.user_data['habit_action'] = update.message.text
    await update.message.reply_text('Enter the new time for the habit or type "quit" to cancel:')
    return EDIT_TIME

async def edit_habit_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == 'quit':
        await update.message.reply_text('Edit operation cancelled.')
        return ConversationHandler.END
    context.user_data['habit_time'] = update.message.text
    await update.message.reply_text('Enter the new place for the habit or type "quit" to cancel:')
    return EDIT_PLACE

async def edit_habit_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == 'quit':
        await update.message.reply_text('Edit operation cancelled.')
        return ConversationHandler.END
    context.user_data['habit_place'] = update.message.text
    habit_id = context.user_data['habit_id']
    action = context.user_data['habit_action']
    time = context.user_data['habit_time']
    place = context.user_data['habit_place']
    headers = {'Authorization': f'Bearer {context.user_data["access_token"]}'}
    payload = {
        'action': action,
        'time': time,
        'place': place,
        'is_public': False,
        'duration': 60,
        'frequency': 1,
        'is_pleasant': False
    }
    response = requests.put(f'{settings.BACKEND_URL}/api/habits/{habit_id}/', headers=headers, data=payload)
    if response.status_code == 200:
        await update.message.reply_text('Habit updated successfully!')
    else:
        await update.message.reply_text('Failed to update habit. Try again.')
    return ConversationHandler.END


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
    await update.message.reply_text('Enter the ID of the habit you want to delete or type "quit" to cancel:')
    return DELETE_HABIT_ID


async def delete_habit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == 'quit':
        await update.message.reply_text('Delete operation cancelled.')
        return ConversationHandler.END
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
            CREATE_IS_PLEASANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_is_pleasant)],
            CREATE_PUBLIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_is_public)],
            CREATE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_action)],
            CREATE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit_time)],
            CREATE_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit)],
            CREATE_BOUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, bind_pleasant_habit)],
            CHOOSE_OR_CREATE_PLEASANT_HABIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_or_create_pleasant_habit)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    edit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('edit', start_edit_habit)],
        states={
            EDIT_HABIT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_id)],
            EDIT_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_action)],
            EDIT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_time)],
            EDIT_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_habit_place)],
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

    list_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('list', start_list_habits)],
        states={
            LIST_PAGINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, paginate_list_habits)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    pub_list_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('pub_list', start_list_public_habits)],
        states={
            PUB_LIST_PAGINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, paginate_list_public_habits)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(register_conv_handler)
    application.add_handler(login_conv_handler)
    application.add_handler(create_conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(delete_conv_handler)
    application.add_handler(list_conv_handler)
    application.add_handler(pub_list_conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()
