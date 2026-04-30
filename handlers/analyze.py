import io
from telegram import Update
from telegram.ext import ContextTypes
import PyPDF2
from services.gemini_api import get_client

async def request_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📄 <b>Відправ мені своє резюме у форматі PDF!</b>\n\n"
        "Я прожену його через наш AI-сканер, оціню за стандартами ATS "
        "(Applicant Tracking System) і скажу, що саме відлякує рекрутерів. 🕵️‍♂️"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode='HTML')
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode='HTML')

async def handle_pdf_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("⏳ <i>Сканую твій PDF... Шукаю червоні прапорці 🚩</i>", parse_mode='HTML')
    
    file = await update.message.document.get_file()
    downloaded_file = await file.download_as_bytearray()
    
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(downloaded_file))
        cv_text = ""
        for page in reader.pages:
            cv_text += page.extract_text()
            
        if len(cv_text.strip()) < 50:
            await message.edit_text("❌ <b>Помилка:</b> Не вдалося прочитати текст з PDF. Можливо, це відсканована картинка?", parse_mode='HTML')
            return
            
        feedback = await analyze_cv_with_ai(cv_text)
        
        await message.edit_text(feedback, parse_mode='HTML')
        
    except Exception as e:
        await message.edit_text(f"❌ <b>Помилка обробки файлу:</b>\n{e}", parse_mode='HTML')

async def analyze_cv_with_ai(text):
    client = get_client()
    
    prompt = f"""Ти — суворий Tech Recruiter та ATS-система (Applicant Tracking System).
    Твоє завдання — жорстко, але конструктивно оцінити резюме кандидата.
    
    ЗАБОРОНЕНО переказувати зміст резюме! Мені не потрібен опис того, що там написано.
    Я хочу бачити реальний фідбек, критику та оцінку.
    
    Формат відповіді (використовуй HTML теги <b>, <i>, <u>):
    📊 <b>ATS Score:</b> [Оцінка від 0 до 100]/100
    <i>[Коротке пояснення оцінки в 1-2 речення]</i>

    ✅ <b>Що зроблено круто:</b>
    • [Пункт 1]
    • [Пункт 2]

    🚩 <b>Червоні прапорці (Що ріже око):</b>
    • [Критика 1 - наприклад, вода в тексті, відсутність метрик]
    • [Критика 2 - проблеми з форматуванням або контактами]

    🛠 <b>Як покращити (Конкретні дії):</b>
    • [Порада 1]
    • [Порада 2]
    
    Ось текст резюме для аналізу:
    {text}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Помилка генерації AI: {e}"