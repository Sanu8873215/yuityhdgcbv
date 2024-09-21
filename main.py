import os
import httpx
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load your Telegram bot token from an environment variable
TELEGRAM_TOKEN = '7995186160:AAFNvDeV8kz6-bFfvLukZWJ-EydA01kOp70'  # Replace with your actual token
CHANNEL_USERNAME = '@ccchargev1'  # Your channel username

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name
    user_id = update.effective_user.id

    try:
        is_member = await asyncio.wait_for(is_user_in_channel(user_id), timeout=10)
    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ Checking your channel membership is taking too long. Please try again later.")
        return

    if is_member:
        await update.message.reply_text(
            "WELCOME TO CHARGEV1\n\n"
            "COMMANDS\n\n"
            "/chk CCNUM|MONTH|YEAR|CVV\n\n"
            "BOT DEVELOPED BY @noobdealer"
        )
    else:
        welcome_text = (
            f"🤖 Bot Status ⇾ Operational ✅\n"
            f"Welcome {user_first_name} To Charge V1 Bot\n"
            f"Don't forget to join 👉 here for announcements and updates!"
        )
        keyboard = [[InlineKeyboardButton("Join Channel", url="https://t.me/ccchargev1")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def is_user_in_channel(user_id: int) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}',
                timeout=5  # Set a timeout for the request
            )
            response.raise_for_status()
            return response.json().get("result", {}).get("status") in ["member", "administrator", "creator"]
        except httpx.HTTPStatusError as http_err:
            print(f"HTTP error: {http_err}")
            return False
        except Exception as e:
            print(f"Error checking channel membership: {e}")
            return False

async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /chk NUM|MONTH|YR|CCC')
        return

    query = context.args[0]
    url = f'http://62.169.23.217/api.php?lista={query}'

    loading_message = await update.message.reply_text(f'Loading from: {url}')

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=3000)  # Set a timeout for the request
            response.raise_for_status()

            response_text = response.text
            if response_text:
                await loading_message.edit_text(f'{response_text}')
            else:
                await loading_message.edit_text('Error: No response content received.')

    except httpx.HTTPStatusError as http_err:
        await loading_message.edit_text(f'HTTP error: {http_err}')
    except asyncio.TimeoutError:
        await loading_message.edit_text('Error: The request timed out.')
    except Exception as e:
        await loading_message.edit_text(f'Error: {str(e)}')

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chk", chk))
    application.run_polling()

if __name__ == '__main__':
    main()
