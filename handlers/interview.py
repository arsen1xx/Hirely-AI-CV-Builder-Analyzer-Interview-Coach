from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.gemini_api import get_client

CHOOSE_ROLE, ANSWER_QUESTION = range(2)

async def start_interview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎙️ <b>Вітаю на Mock Interview!</b>\n\nНа яку посаду ти претендуєш? (Наприклад: UI/UX Designer, Frontend, Project Manager)"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode='HTML')
    else:
        await update.message.reply_text(text, parse_mode='HTML')
        
    return CHOOSE_ROLE

async def get_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text
    context.user_data['interview_role'] = role
    
    await update.message.reply_text("⏳ <i>Готую питання як справжній Senior HR... Це займе пару секунд.</i>", parse_mode='HTML')
    
    questions = await generate_interview_questions(role)
    
    if not questions:
        await update.message.reply_text("❌ Сталася помилка при генерації питань. Спробуй ще раз.")
        return ConversationHandler.END
        
    context.user_data['interview_questions'] = questions
    context.user_data['current_q_index'] = 0
    context.user_data['interview_answers'] = []
    
    first_q = questions[0]
    keyboard = ReplyKeyboardMarkup([["🔚 Завершити інтерв'ю"]], resize_keyboard=True)
    
    await update.message.reply_text(
        f"👨‍💼 <b>Питання 1 з {len(questions)}:</b>\n\n{first_q}", 
        parse_mode='HTML',
        reply_markup=keyboard
    )
    return ANSWER_QUESTION

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    questions = context.user_data['interview_questions']
    idx = context.user_data['current_q_index']
    
    context.user_data['interview_answers'].append({
        "question": questions[idx],
        "answer": answer
    })
    
    idx += 1
    context.user_data['current_q_index'] = idx
    
    if idx < len(questions):
        next_q = questions[idx]
        await update.message.reply_text(
            f"👨‍💼 <b>Питання {idx+1} з {len(questions)}:</b>\n\n{next_q}", 
            parse_mode='HTML'
        )
        return ANSWER_QUESTION
    else:
        await update.message.reply_text(
            "🏁 <b>Інтерв'ю завершено! Дякую за твої відповіді.</b>\n\n"
            "⏳ <i>Аналізую твій виступ та готую розгорнутий фідбек...</i>", 
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )
        
        feedback = await evaluate_interview(
            context.user_data['interview_role'], 
            context.user_data['interview_answers']
        )
        
        await update.message.reply_text(feedback, parse_mode='HTML')
        return ConversationHandler.END

async def stop_interview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛑 Інтерв'ю перервано. Тисни /start для повернення в меню.", 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def generate_interview_questions(role):
    client = get_client()
    prompt = f"""Ти — Senior Tech Recruiter. Проведи співбесіду на посаду {role}.
    Згенеруй рівно 4 реалістичні питання для кандидата. 
    Питання мають бути складними, ситуативними, без банальщини (не питай "ким ви бачите себе через 5 років").
    
    Структура:
    1. Soft-skills / Досвід роботи
    2. Hard-skills / Технології
    3. Продуктове мислення / UX (або вирішення архітектурних проблем)
    4. Поведінкове питання (конфлікт або складна задача)
    
    Поверни ТІЛЬКИ текст питань. Розділяй їх символами '|||'.
    Приклад: Розкажіть про свій найскладніший проєкт.|||Як ви підходите до...|||Що будете робити, якщо...|||Як тестуєте...
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in text.split('|||') if q.strip()]
        
        if len(questions) < 2:
            questions = [q.strip() for q in text.split('\n') if q.strip() and not q.lower().startswith('ось')]
            
        return questions[:4]
    except:
        return ["Розкажи про свій досвід.", "Які інструменти ти використовуєш найчастіше?", "Як вирішуєш конфлікти в команді?", "Опиши свій процес роботи над задачею."]

async def evaluate_interview(role, qa_pairs):
    client = get_client()
    
    qa_text = ""
    for i, pair in enumerate(qa_pairs, 1):
        qa_text += f"Q{i}: {pair['question']}\nВідповідь: {pair['answer']}\n\n"
        
    prompt = f"""Ти — Senior Tech HR. Оціни відповіді кандидата на посаду {role}.
    Ти маєш дати жорсткий, професійний, але підтримуючий фідбек.
    
    Ось як пройшла співбесіда (питання та відповіді):
    {qa_text}
    
    Формат відповіді:
    🎯 <b>Загальне враження:</b> [Твій чесний коментар як HR]
    📊 <b>Оцінка:</b> [Х/10]
    
    ✅ <b>Що було круто:</b>
    • [Сильні сторони у відповідях]
    
    🚩 <b>Що треба підтягнути (Помилки або слабкі місця):</b>
    • [Що кандидат сказав не так, де не вистачило конкретики]
    
    💡 <b>Порада від рекрутера:</b> [Як краще відповідати наступного разу]
    
    Використовуй HTML теги <b>, <i>. Нічого зайвого, без води.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Помилка при генерації фідбеку: {e}"