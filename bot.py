import logging
import os
import sys
from dotenv import load_dotenv
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ ПОМИЛКА: TELEGRAM_TOKEN не знайдено!")
    sys.exit(1)

try:
    from handlers.menu import start_command
    from handlers.analyze import handle_pdf_analysis, request_pdf
    from handlers.profile import (
        start_profile, profile_action, handle_profile_input, PROF_DASHBOARD, PROF_WAIT_INPUT
    )
    from handlers.create_cv import (
        start_cv_generation, toggle_cv_section, final_build_cv, download_pdf_action, SELECT_SECTIONS
    )
    from handlers.interview import (
        start_interview, get_role, handle_answer, stop_interview, CHOOSE_ROLE, ANSWER_QUESTION
    )
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main():
    application = Application.builder().token(TOKEN).build()

    profile_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_profile, pattern="^menu_settings$")],
        states={
            PROF_DASHBOARD: [CallbackQueryHandler(profile_action, pattern="^prof_")],
            PROF_WAIT_INPUT: [
                CallbackQueryHandler(profile_action, pattern="^prof_back$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_profile_input)
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        allow_reentry=True,
        per_message=False
    )

    gen_cv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_cv_generation, pattern="^menu_build_cv$")],
        states={
            SELECT_SECTIONS: [
                CallbackQueryHandler(toggle_cv_section, pattern="^toggle_"),
                CallbackQueryHandler(final_build_cv, pattern="^final_generate$"),
                CallbackQueryHandler(start_command, pattern="^menu_back$")
            ]
        },
        fallbacks=[CommandHandler("start", start_command)],
        allow_reentry=True,
        per_message=False
    )

    interview_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_interview, pattern="^menu_mock_interview$"),
            CommandHandler("interview", start_interview)
        ],
        states={
            CHOOSE_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_role)],
            ANSWER_QUESTION: [
                MessageHandler(filters.Regex("^🔚 Завершити інтерв'ю$"), stop_interview),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        allow_reentry=True,
        per_message=False
    )
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("analyze", request_pdf))
    
    application.add_handler(profile_handler)
    application.add_handler(gen_cv_handler)
    application.add_handler(interview_handler)

    application.add_handler(CallbackQueryHandler(request_pdf, pattern="^menu_analyze_cv$"))
    application.add_handler(CallbackQueryHandler(download_pdf_action, pattern="^download_pdf$"))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf_analysis))

    print("🚀 Hirely Bot запущено успішно...")
    application.run_polling()

if __name__ == '__main__':
    main()