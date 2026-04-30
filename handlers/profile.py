from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

PROF_DASHBOARD, PROF_WAIT_INPUT = range(2)

async def start_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            'name': 'Не вказано',
            'contacts': {'phone': '', 'email': '', 'linkedin': '', 'other': ''},
            'summary': 'Не вказано',
            'experience': [],
            'projects': [],
            'skills': 'Не вказано',
            'education': [],
            'custom': {}
        }
    
    await show_profile_dashboard(update, context)
    return PROF_DASHBOARD

async def show_profile_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prof = context.user_data['profile']
    
    c = prof['contacts']
    c_list = [v for v in [c['phone'], c['email'], c['linkedin'], c['other']] if v]
    c_str = " | ".join(c_list) if c_list else "Не вказано"
    
    text = f"⚙️ <b>ТВІЙ ПРОФІЛЬ КАНДИДАТА</b>\n\n"
    text += f"👤 <b>Ім'я:</b> {prof['name']}\n"
    text += f"📞 <b>Контакти:</b> {c_str}\n"
    text += f"📝 <b>Summary:</b> {prof['summary'][:50]}...\n\n"
    text += f"💼 <b>Досвід:</b> {len(prof['experience'])} записів\n"
    text += f"🚀 <b>Проєкти:</b> {len(prof['projects'])} записів\n"
    text += f"🎓 <b>Освіта:</b> {len(prof['education'])} записів\n"
    text += f"🛠 <b>Навички:</b> {prof['skills']}\n"
    
    for c_name, c_items in prof['custom'].items():
        text += f"📌 <b>{c_name}:</b> {len(c_items)} записів\n"

    text += "\n<i>Обери розділ для заповнення:</i>"

    keyboard = [
        [InlineKeyboardButton("👤 Ім'я", callback_data="prof_edit_name"), 
         InlineKeyboardButton("📞 Контакти (Окремо)", callback_data="prof_menu_contacts")],
        [InlineKeyboardButton("📝 Профіль (Summary)", callback_data="prof_edit_summary")],
        [InlineKeyboardButton("💼 + Додати Досвід", callback_data="prof_add_exp_title"),
         InlineKeyboardButton("🚀 + Додати Проєкт", callback_data="prof_add_proj_name")],
        [InlineKeyboardButton("🎓 + Додати Освіту", callback_data="prof_add_edu_uni"),
         InlineKeyboardButton("🛠 Навички", callback_data="prof_edit_skills")]
    ]
    
    for idx, c_name in enumerate(prof['custom'].keys()):
        keyboard.append([InlineKeyboardButton(f"📌 + Додати в {c_name}", callback_data=f"prof_add_custitem_{idx}")])

    keyboard.append([InlineKeyboardButton("➕ Створити новий розділ", callback_data="prof_create_custom")])
    keyboard.append([InlineKeyboardButton("🔙 Повернутися в меню", callback_data="prof_exit")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        except: pass
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def show_contacts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = context.user_data['profile']['contacts']
    text = "📞 <b>НАЛАШТУВАННЯ КОНТАКТІВ</b>\nОбери, що хочеш додати чи змінити:"
    
    keyboard = [
        [InlineKeyboardButton(f"📱 Телефон: {c['phone'] or '❌'}", callback_data="prof_edit_phone")],
        [InlineKeyboardButton(f"📧 Email: {c['email'] or '❌'}", callback_data="prof_edit_email")],
        [InlineKeyboardButton(f"🔗 LinkedIn: {c['linkedin'] or '❌'}", callback_data="prof_edit_linkedin")],
        [InlineKeyboardButton(f"🌐 Інше (Портф.): {c['other'] or '❌'}", callback_data="prof_edit_other")],
        [InlineKeyboardButton("🔙 Назад до профілю", callback_data="prof_back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def profile_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "prof_exit":
        await query.edit_message_text("💾 Профіль збережено! Тисни /start для повернення в головне меню.")
        return ConversationHandler.END
        
    if data == "prof_menu_contacts":
        await show_contacts_menu(update, context)
        return PROF_DASHBOARD
        
    if data == "prof_back_to_main":
        await show_profile_dashboard(update, context)
        return PROF_DASHBOARD

    if data == "prof_back":
        field = context.user_data.get('editing_field', '')
        if 'temp_item' in context.user_data:
            del context.user_data['temp_item']
            
        if field in ["prof_edit_phone", "prof_edit_email", "prof_edit_linkedin", "prof_edit_other"]:
            await show_contacts_menu(update, context)
        else:
            await show_profile_dashboard(update, context)
        return PROF_DASHBOARD
        
    if data.startswith("prof_add_custitem_"):
        idx = int(data.split("_")[-1])
        c_name = list(context.user_data['profile']['custom'].keys())[idx]
        context.user_data['editing_custom_name'] = c_name
        context.user_data['editing_field'] = "prof_add_custitem"
        prompt = f"Введи новий запис для розділу <b>{c_name}</b>:"
    else:
        context.user_data['editing_field'] = data
        context.user_data['temp_item'] = {}
        
        prompts = {
            "prof_edit_name": "Введи своє прізвище та Ім'я:",
            "prof_edit_phone": "Введи номер телефону:",
            "prof_edit_email": "Введи Email:",
            "prof_edit_linkedin": "Введи посилання на LinkedIn:",
            "prof_edit_other": "Введи посилання на портфоліо чи GitHub:",
            "prof_edit_summary": "Напиши короткий опис про себе:",
            "prof_edit_skills": "Введи свої навички через кому:",
            "prof_create_custom": "Введи НАЗВУ нового розділу (наприклад, 'Курси' або 'Мови'):",
            "prof_add_proj_name": "Введи <b>Назву проєкту</b>:",
            "prof_add_exp_title": "Введи <b>Посаду</b> (напр. UI/UX Designer):",
            "prof_add_edu_uni": "Введи <b>Назву Університету або Курсів</b>:"
        }
        prompt = prompts.get(data, "Введи дані:")
    
    keyboard = [[InlineKeyboardButton("🔙 Скасувати", callback_data="prof_back")]]
    await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return PROF_WAIT_INPUT

async def handle_profile_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    field = context.user_data.get('editing_field')
    prof = context.user_data['profile']
    
    if field == "prof_edit_name": prof['name'] = text
    elif field == "prof_edit_summary": prof['summary'] = text
    elif field == "prof_edit_skills": prof['skills'] = text
    
    elif field in ["prof_edit_phone", "prof_edit_email", "prof_edit_linkedin", "prof_edit_other"]:
        key = field.split("_")[-1]
        prof['contacts'][key] = text
        await show_contacts_menu(update, context)
        return PROF_DASHBOARD
        
    elif field == "prof_create_custom":
        if text not in prof['custom']: prof['custom'][text] = []
    elif field == "prof_add_custitem":
        c_name = context.user_data['editing_custom_name']
        prof['custom'][c_name].append(text)

    elif field == "prof_add_proj_name":
        context.user_data['temp_item']['name'] = text
        context.user_data['editing_field'] = "prof_add_proj_desc"
        await update.message.reply_text("Чудово! Тепер напиши короткий <b>Опис проєкту</b> (що він робить):", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_proj_desc":
        context.user_data['temp_item']['desc'] = text
        context.user_data['editing_field'] = "prof_add_proj_stack"
        await update.message.reply_text("Супер! Тепер вкажи <b>Стек технологій</b> (напр. Figma, React, Python):", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_proj_stack":
        t = context.user_data['temp_item']
        formatted_proj = f"{t['name']} — {t['desc']}. Стек: {text}"
        prof['projects'].append(formatted_proj)

    elif field == "prof_add_exp_title":
        context.user_data['temp_item']['title'] = text
        context.user_data['editing_field'] = "prof_add_exp_company"
        await update.message.reply_text("Вкажи <b>Назву компанії</b>:", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_exp_company":
        context.user_data['temp_item']['company'] = text
        context.user_data['editing_field'] = "prof_add_exp_years"
        await update.message.reply_text("Вкажи <b>Роки роботи</b> (напр. 2022 - 2024 або 2023 - дотепер):", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_exp_years":
        context.user_data['temp_item']['years'] = text
        context.user_data['editing_field'] = "prof_add_exp_desc"
        await update.message.reply_text("Опиши свої <b>Обов'язки та Досягнення</b>:", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_exp_desc":
        t = context.user_data['temp_item']
        formatted_exp = f"{t['title']} в {t['company']} ({t['years']}) — {text}"
        prof['experience'].append(formatted_exp)

    elif field == "prof_add_edu_uni":
        context.user_data['temp_item']['uni'] = text
        context.user_data['editing_field'] = "prof_add_edu_spec"
        await update.message.reply_text("Вкажи <b>Спеціальність</b> (напр. Інженерія ПЗ):", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_edu_spec":
        context.user_data['temp_item']['spec'] = text
        context.user_data['editing_field'] = "prof_add_edu_years"
        await update.message.reply_text("Вкажи <b>Роки навчання</b> (напр. 2023 - 2027):", parse_mode='HTML')
        return PROF_WAIT_INPUT
    elif field == "prof_add_edu_years":
        t = context.user_data['temp_item']
        formatted_edu = f"{t['uni']}, {t['spec']} ({text})"
        prof['education'].append(formatted_edu)

    if 'temp_item' in context.user_data:
        del context.user_data['temp_item']
    
    await show_profile_dashboard(update, context)
    return PROF_DASHBOARD