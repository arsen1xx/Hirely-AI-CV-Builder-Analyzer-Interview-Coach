import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from fpdf import FPDF

SELECT_SECTIONS = "SELECT_SECTIONS"

async def start_cv_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    prof = context.user_data.get('profile')
    
    if not prof or prof['name'] == 'Не вказано':
        keyboard = [[InlineKeyboardButton("⚙️ Налаштувати профіль", callback_data="menu_settings")]]
        await query.edit_message_text(
            "❌ <b>Твій профіль порожній!</b>\n\nСпочатку вкажи хоча б своє ім'я в налаштуваннях.",
            parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    if 'cv_selection' not in context.user_data:
        context.user_data['cv_selection'] = {
            'summary': True if prof['summary'] != 'Не вказано' else False,
            'experience': True if prof['experience'] else False,
            'projects': True if prof['projects'] else False,
            'skills': True if prof['skills'] != 'Не вказано' else False,
            'education': True if prof['education'] else False,
            'custom': True if prof['custom'] else False
        }
    
    await show_selection_menu(update, context)
    return SELECT_SECTIONS

async def show_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sel = context.user_data['cv_selection']
    
    text = (
        "🎯 <b>Налаштування твого резюме</b>\n\n"
        "Обери розділи, які ти хочеш бачити у фінальному файлі. "
        "Клікай на кнопки, щоб увімкнути або вимкнути блок:"
    )
    
    status = lambda field: "✅" if sel.get(field) else "❌"
    
    keyboard = [
        [InlineKeyboardButton(f"{status('summary')} Профіль (Summary)", callback_data="toggle_summary")],
        [InlineKeyboardButton(f"{status('experience')} Досвід роботи", callback_data="toggle_experience")],
        [InlineKeyboardButton(f"{status('projects')} Проєкти", callback_data="toggle_projects")],
        [InlineKeyboardButton(f"{status('skills')} Навички", callback_data="toggle_skills")],
        [InlineKeyboardButton(f"{status('education')} Освіта", callback_data="toggle_education")],
        [InlineKeyboardButton(f"{status('custom')} Додаткові розділи", callback_data="toggle_custom")],
        [InlineKeyboardButton("🚀 ЗГЕНЕРУВАТИ PDF", callback_data="final_generate")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_back")]
    ]
    
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def toggle_cv_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    field = query.data.replace("toggle_", "")
    context.user_data['cv_selection'][field] = not context.user_data['cv_selection'][field]
    
    await show_selection_menu(update, context)
    return SELECT_SECTIONS

async def final_build_cv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    prof = context.user_data['profile']
    
    text = f"✅ <b>Майже готово!</b>\n\nВсі дані успішно зібрані для {prof['name']}. Тисни кнопку нижче, щоб згенерувати та завантажити свій стильний PDF-файл з шрифтом Inter. ✨"
    
    keyboard = [
        [InlineKeyboardButton("📥 Завантажити PDF", callback_data="download_pdf")],
        [InlineKeyboardButton("🔙 Головне меню", callback_data="menu_back")]
    ]
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def download_pdf_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Створення та відправка реального PDF файлу зі шрифтом Inter"""
    query = update.callback_query
    await query.answer()
    
    prof = context.user_data.get('profile')
    sel = context.user_data.get('cv_selection', {})
    
    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.add_font("Inter", "", "Inter-Regular.ttf")
        pdf.add_font("Inter", "B", "Inter-Bold.ttf")
    except Exception as e:
        await query.message.reply_text(
            "⚠️ <b>Помилка шрифту:</b> Файли <code>Inter-Regular.ttf</code> та <code>Inter-Bold.ttf</code> не знайдено!\n"
            "Будь ласка, переконайся, що вони лежать у тій самій папці, де знаходиться файл bot.py.", 
            parse_mode='HTML'
        )
        return

    pdf.set_font("Inter", "B", 22)
    pdf.cell(0, 10, prof['name'].upper(), align='C', new_x="LMARGIN", new_y="NEXT")
    
    c = prof['contacts']
    c_list = [v for v in [c['phone'], c['email'], c['linkedin'], c['other']] if v]
    if c_list:
        pdf.set_font("Inter", "", 10)
        pdf.cell(0, 6, " | ".join(c_list), align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(8)
    
    def add_section(title, content_list, is_text=False):
        pdf.set_font("Inter", "B", 14)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.line(pdf.get_x(), pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font("Inter", "", 11)
        if is_text:
            pdf.multi_cell(0, 6, content_list, new_x="LMARGIN", new_y="NEXT")
        else:
            for item in content_list:
                pdf.multi_cell(0, 6, f"• {item}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

    if sel.get('summary') and prof['summary'] != 'Не вказано':
        add_section("ПРОФІЛЬ", prof['summary'], is_text=True)
        
    if sel.get('experience') and prof['experience']:
        add_section("ДОСВІД РОБОТИ", prof['experience'])
        
    if sel.get('projects') and prof['projects']:
        add_section("ПРОЄКТИ", prof['projects'])
        
    if sel.get('skills') and prof['skills'] != 'Не вказано':
        add_section("НАВИЧКИ", prof['skills'], is_text=True)
        
    if sel.get('education') and prof['education']:
        add_section("ОСВІТА", prof['education'])
        
    if sel.get('custom') and prof['custom']:
        for c_name, c_items in prof['custom'].items():
            if c_items:
                add_section(c_name.upper(), c_items)

    pdf_bytes = pdf.output()
    file_buffer = io.BytesIO(pdf_bytes)
    file_buffer.name = f"CV_{prof['name'].replace(' ', '_')}.pdf"
    
    await query.message.reply_document(
        document=file_buffer,
        caption="📄 Твоє професійне резюме готове! Успіхів з відгуками на вакансії! 🚀"
    ),