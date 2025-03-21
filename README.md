![German Learning Bot](./images/an%20image%20for%20the%20app%20GermanLearningBot.png)

# German Learning Bot 🇩🇪

> A Telegram bot helping users learn German through interactive conversations, vocabulary, quizzes, and AI assistance.

## ✨ Features

- **🎯 Multi-level proficiency** - Comprehensive support from A1 (beginner) to C2 (mastery) levels
- **🗣️ Conversation practice** - Learn through contextual dialogues with translations
- **📚 Vocabulary builder** - Expand your German vocabulary with examples and translations
- **🧠 Interactive quizzes** - Test your knowledge with adaptive multiple-choice questions
- **🤖 AI language tutor** - Get personalized assistance from an AI German teacher
- **🌐 Bilingual interface** - Instructions in both German and Persian

## 🛠️ Technologies

- **Python** - Core programming language
- **python-telegram-bot** - Framework for Telegram bot functionality
- **OpenRouter API** - AI service for generating language learning content
- **SQLite** - Local database for conversation history and user preferences
- **python-dotenv** - Environment variable management

## 📋 Prerequisites

- Python 3.7+
- Telegram Bot Token (from [BotFather](https://t.me/botfather))
- OpenRouter API Key (from [openrouter.ai](https://openrouter.ai))

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/GermanLearningBot.git
   cd GermanLearningBot
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:

   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

## 💻 Usage

1. **Start the bot**

   ```bash
   python Telegram_Bot.py
   ```

2. **Interact with the bot on Telegram**
   - Start a conversation with the bot using the `/start` command
   - Select your German proficiency level (A1-C2)
   - Choose from conversation practice, vocabulary learning, quizzes, or AI teacher

## 📊 Learning Workflow

1. **Choose your level** - Select from A1 (beginner) to C2 (mastery)
2. **Pick a learning mode**:
   - **Conversations** - Practice with realistic dialogues
   - **Vocabulary** - Learn new words with context
   - **Quiz** - Test your knowledge
   - **AI Teacher** - Get personalized assistance

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Have questions? Open an issue or contact the repository owner.

---

_Viel Spaß beim Deutschlernen!_ (Have fun learning German!)
