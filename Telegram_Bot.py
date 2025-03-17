from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from openrouter_api import ask_openrouter
from db import save_message, get_conversation_history

# ======= CONFIGURATION ========

# ... existing code ...

# ======= CONFIGURATION ========
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_default_token_here")

# ======= START COMMAND ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # مرحله اول: انتخاب سطح زبان
    keyboard = [
        [InlineKeyboardButton("🟢 A1 - Anfänger", callback_data='A1')],
        [InlineKeyboardButton("🟡 A2 - Anfänger", callback_data='A2')],
        [InlineKeyboardButton("🟠 B1 - Mittelstufe", callback_data='B1')],
        [InlineKeyboardButton("🔵 B2 - Mittelstufe", callback_data='B2')],
        [InlineKeyboardButton("🟣 C1 - Fortgeschritten", callback_data='C1')],
        [InlineKeyboardButton("⚫ C2 - Meister", callback_data='C2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Willkommen beim Deutsch-Lernbot! 🎉\n"
        "Bitte wähle dein Niveau (سطح خود را انتخاب کن):",
        reply_markup=reply_markup
    )

    # Save initial state (waiting for level choice)
    context.user_data['state'] = 'choose_level'


# ======= BUTTON HANDLER ========
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data  # The callback data passed from the button

    # Handle level selection
    if choice in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        context.user_data['level'] = choice  # Save level
        context.user_data['state'] = 'level_selected'

        # Show practice options
        keyboard = [
            [InlineKeyboardButton("1. Konversation (مکالمه)", callback_data='konversation')],
            [InlineKeyboardButton("2. Vokabeln (لغات)", callback_data='vokabeln')],
            [InlineKeyboardButton("3. Quiz (آزمون)", callback_data='quiz')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=(
                f"Du hast {choice} gewählt. (شما سطح {choice} را انتخاب کردید)\n"
                "Was möchtest du jetzt üben?\n"
                "1. Konversation (مکالمه)\n"
                "2. Vokabeln (لغات)\n"
                "3. Quiz (آزمون)"
            ),
            reply_markup=reply_markup
        )
        await query.answer()
        return

    # Handle other options after level is selected
    if choice == 'konversation':
        await query.answer()
        await start_conversation(query, context)
    
    elif choice == 'vokabeln':
        await query.answer()
        await start_vocabulary(query, context)
    
    elif choice == 'quiz':
        await query.answer()
        await start_quiz(query, context)
    
    # Fix: Changed 'if' to 'elif' to properly handle button callbacks
    elif choice == 'next_word':
        await query.answer()
        await start_vocabulary(query, context)
        
    elif choice == 'next_dialog':
        await query.answer()
        await start_conversation(query, context)
    
    # Add quiz answer handling
    elif choice.startswith('quiz_answer_'):
        await query.answer()
        answer_index = int(choice.split('_')[-1])
        await check_quiz_answer(query, context, answer_index)


# ======= CONVERSATION ========
async def start_conversation(query, context):
    level = context.user_data.get('level', 'A1')
    
    prompt = f"""Create a single short German dialogue for level {level}. Respond in exactly this format:
Title|Persian Title|Dialog|Translation

Example:
Im Café|در کافه|A: Guten Tag! B: Hallo!|A: Hello! B: Hi!

Important: Give only ONE dialogue, no additional examples or text."""
    
    try:
        response = await ask_openrouter(prompt, purpose="conversation")
        if '|' not in response:
            raise ValueError("Invalid response format")
            
        # Improved parsing to handle complex responses
        # First, try to extract just the first line if there are multiple lines
        first_line = response.split('\n')[0].strip()
        
        # If we still have too many parts, try to intelligently extract the 4 components
        if first_line.count('|') >= 3:
            # Extract the first two parts normally
            parts = first_line.split('|')
            title_de = parts[0].strip()
            title_fa = parts[1].strip()
            
            # For the dialog and translation, which might contain | characters,
            # we'll use a more robust approach
            remaining = '|'.join(parts[2:])
            
            # Find the last occurrence of | which should separate dialog and translation
            last_pipe_index = remaining.rindex('|')
            dialog = remaining[:last_pipe_index].strip()
            translation = remaining[last_pipe_index+1:].strip()
        else:
            # If the response doesn't have enough | characters, try a fallback approach
            raise ValueError("Response doesn't contain enough separators")
        
        keyboard = [[InlineKeyboardButton("▶️ Nächster Dialog (مکالمه بعدی)", callback_data='next_dialog')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"🗣 {title_de}\n({title_fa})\n\n"
                 f"🇩🇪 {dialog}\n\n"
                 f"🔸 {translation}",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Conversation Error: {str(e)}")
        # Don't print the full response as it might be very long
        print(f"Response excerpt: {response[:100]}..." if 'response' in locals() else "No response received")
        
        # Send a more user-friendly error message and offer to try again
        keyboard = [[InlineKeyboardButton("🔄 Erneut versuchen (تلاش مجدد)", callback_data='konversation')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="⚠️ Es gab ein Problem mit dem Dialog. Bitte versuche es erneut. (مشکلی در ایجاد مکالمه پیش آمد. لطفا دوباره تلاش کنید.)",
            reply_markup=reply_markup
        )

# ======= VOCABULARY ========
async def start_vocabulary(query, context):
    level = context.user_data.get('level', 'A1')
    
    prompt = f"""Give me a single German word for level {level}. Respond in exactly this format:
Word|Meaning|Example|Translation

Example:
der Hund|dog|Der Hund ist klein.|The dog is small.

Important: Give only ONE word, no additional examples or text."""
    
    try:
        response = await ask_openrouter(prompt, purpose="vocabulary")
        if '|' not in response:
            raise ValueError("Invalid response format")
            
        # Improved parsing to handle complex responses
        # First, try to extract just the first line if there are multiple lines
        first_line = response.split('\n')[0].strip()
        
        # If we still have too many parts, try to intelligently extract the 4 components
        if first_line.count('|') >= 3:
            # Extract the first two parts normally
            parts = first_line.split('|')
            word = parts[0].strip()
            meaning = parts[1].strip()
            
            # For the example and translation, which might contain | characters,
            # we'll use a more robust approach
            remaining = '|'.join(parts[2:])
            
            # Find the last occurrence of | which should separate example and translation
            last_pipe_index = remaining.rindex('|')
            example = remaining[:last_pipe_index].strip()
            translation = remaining[last_pipe_index+1:].strip()
        else:
            # If the response doesn't have enough | characters, try a fallback approach
            raise ValueError("Response doesn't contain enough separators")
        
        keyboard = [[InlineKeyboardButton("▶️ Nächstes Wort (کلمه بعدی)", callback_data='next_word')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"📚 {word}\n"
                 f"🔸 {meaning}\n"
                 f"📝 {example}\n"
                 f"🔸 {translation}",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Vocabulary Error: {str(e)}")
        # Don't print the full response as it might be very long
        print(f"Response excerpt: {response[:100]}..." if 'response' in locals() else "No response received")
        
        # Send a more user-friendly error message and offer to try again
        keyboard = [[InlineKeyboardButton("🔄 Erneut versuchen (تلاش مجدد)", callback_data='vokabeln')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="⚠️ Es gab ein Problem mit dem Vokabel. Bitte versuche es erneut. (مشکلی در ایجاد لغت پیش آمد. لطفا دوباره تلاش کنید.)",
            reply_markup=reply_markup
        )


# ======= QUIZ ========
async def start_quiz(query, context):
    level = context.user_data.get('level', 'A1')
    
    prompt = f"""Create a German language quiz question for level {level}. Respond in exactly this format:
Question|Option1|Option2|Option3|Option4|CorrectIndex|Explanation

Example:
Was bedeutet "Hund" auf Englisch?|dog|cat|house|car|1|"Hund" means "dog" in English.

Important: CorrectIndex should be 1, 2, 3, or 4 (not 0-based). Give only ONE question, no additional text."""
    
    try:
        response = await ask_openrouter(prompt, purpose="quiz")
        if '|' not in response:
            raise ValueError("Invalid response format")
            
        # Improved parsing to handle complex responses
        # First, try to extract just the first line if there are multiple lines
        first_line = response.split('\n')[0].strip()
        
        # Extract parts, ensuring we have at least 7 components
        parts = first_line.split('|')
        if len(parts) < 7:
            raise ValueError(f"Not enough parts in response, got {len(parts)}")
            
        question = parts[0].strip()
        option1 = parts[1].strip()
        option2 = parts[2].strip()
        option3 = parts[3].strip()
        option4 = parts[4].strip()
        
        # The correct index should be a number
        try:
            correct_index = int(parts[5].strip())
            if correct_index < 1 or correct_index > 4:
                raise ValueError(f"CorrectIndex should be between 1 and 4, got {correct_index}")
        except ValueError:
            # If we can't parse the correct index, default to 1
            correct_index = 1
            print(f"Warning: Could not parse correct index '{parts[5]}', defaulting to 1")
        
        # The explanation is everything after the correct index
        explanation = '|'.join(parts[6:]).strip()
        
        # Store the correct answer and explanation in user_data for checking later
        context.user_data['quiz_correct_index'] = correct_index
        context.user_data['quiz_explanation'] = explanation
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(f"1. {option1}", callback_data='quiz_answer_1')],
            [InlineKeyboardButton(f"2. {option2}", callback_data='quiz_answer_2')],
            [InlineKeyboardButton(f"3. {option3}", callback_data='quiz_answer_3')],
            [InlineKeyboardButton(f"4. {option4}", callback_data='quiz_answer_4')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"📝 Quiz: {question}",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Quiz Error: {str(e)}")
        # Don't print the full response as it might be very long
        print(f"Response excerpt: {response[:100]}..." if 'response' in locals() else "No response received")
        
        # Send a more user-friendly error message and offer to try again
        keyboard = [[InlineKeyboardButton("🔄 Erneut versuchen (تلاش مجدد)", callback_data='quiz')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="⚠️ Es gab ein Problem. Bitte versuche es erneut. (مشکلی پیش آمد. لطفا دوباره تلاش کنید.)"
        )

# Add function to check quiz answers
async def check_quiz_answer(query, context, answer_index):
    correct_index = context.user_data.get('quiz_correct_index')
    explanation = context.user_data.get('quiz_explanation', 'No explanation available')
    
    if answer_index == correct_index:
        result_text = "✅ Richtig! (درست!)\n\n" + explanation
    else:
        result_text = f"❌ Falsch. Die richtige Antwort ist {correct_index}. (نادرست. پاسخ صحیح {correct_index} است.)\n\n" + explanation
    
    # Add button for next quiz
    keyboard = [[InlineKeyboardButton("▶️ Nächstes Quiz (آزمون بعدی)", callback_data='quiz')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=result_text,
        reply_markup=reply_markup
    )


# ======= MAIN =========
if __name__ == '__main__':
    try:
        print("Starting German Learning Bot...")
        print("Initializing application with token...")
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        print("Adding command handlers...")
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CallbackQueryHandler(button))

        print("✅ Bot is running... Press Ctrl+C to stop")
        app.run_polling()
    except Exception as e:
        print(f"❌ Error starting bot: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPlease check your configuration and dependencies.")
        input("Press Enter to exit...")
