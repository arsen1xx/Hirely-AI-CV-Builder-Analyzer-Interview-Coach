from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    keyboard = [
        [InlineKeyboardButton("📝 Створити CV з нуля", callback_data="menu_build_cv")],
        [InlineKeyboardButton("📊 Рев'ю мого PDF (AI Аналіз)", callback_data="menu_analyze_cv")],
        [InlineKeyboardButton("🎙️ Пройти Mock Interview", callback_data="menu_mock_interview")],
        [InlineKeyboardButton("⚙️ Налаштування профілю", callback_data="menu_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🚀 <b>Hirely: Твій кар'єрний помічник</b>\n\n"
        "Привіт! Я - твій персональний кар'єрний копілот. "
        "Поки інші розсилають сотні однакових резюме, ми з тобою зробимо "
        "<b>оффер-магніт</b>, який пройде через будь-які фільтри рекрутерів. ✨\n\n"
        "<b>Що ми сьогодні прокачаємо?</b>\n"
        "• Зберемо професійне CV за 5 хвилин\n"
        "• Розберемо твій CV та знайдемо помилки\n"
        "• Потренуємось відповідати на підступні питання HR\n\n"
        "<i>Обирай розділ нижче і почнемо рух до твого мільйона! 💸</i>"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    elif update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        except:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')