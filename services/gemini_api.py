
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("❌ GROQ_API_KEY не знайдено!")
    return Groq(api_key=api_key)

def generate_cv_summary(draft_text: str, position: str) -> str:
    """Генерує крутий опис про себе (Summary)"""
    client = get_client()
    prompt = f"""
    Ти — соковитий копірайтер та дизайнер. Твоя задача: перетворити цей чорновик на професійне Summary для резюме.
    Посада: {position}
    Чорновик: "{draft_text}"
    
    ПРАВИЛА:
    1. Пиши українською, стильно, без води. ✨
    2. Використовуй IT-сленг.
    3. Зроби текст лаконічним (2-3 речення).
    4. Видай ТІЛЬКИ текст опису.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return draft_text

def analyze_cv_text(text: str) -> str:
    client = get_client()
    # Промпт, який не дає ШІ розслабитися
    prompt = f"""
    Ти — Senior Product Designer. Тобі дали текст резюме для жорсткого та швидкого рев'ю.
    
    СУВОРІ ОБМЕЖЕННЯ:
    1. ЗАБОРОНЕНО вітатися, представлятися або писати вступні фрази ("Ось поради", "Як рекрутер я пропоную").
    2. Одразу переходить до пунктів 1, 2, 3.
    3. Ніякої вигаданої дічі про мови чи структуру. Пиши ТІЛЬКИ про зміст досвіду та навички. 🚀
    4. Використовуй відповідний сленг: Design System, Stakeholders, Prototyping, ATS-friendly.
    5. Використовуй емодзі та виділяй головне <b>жирним</b> через HTML-теги.
    
    Ось текст резюме:
    {text}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            # Це найрозумніша модель в Groq на даний момент
            model="llama-3.3-70b-versatile",
            temperature=0.3 # Низька температура = менше фантазій і більше діла
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Помилка AI: {e}"