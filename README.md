# Mental Health Chatbot

MindfulAI is a compassionate, empathetic mental health support chatbot designed to provide emotional support and understanding. It uses advanced natural language processing models to engage users in meaningful conversations, helping them explore their feelings in a safe and supportive environment.

## Features
- Emotion detection to tailor responses
- Empathetic and supportive conversation flow
- Follow-up questions based on detected emotions
- Short, meaningful responses to encourage sharing
- Safe, non-judgmental space for users

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mindfulai-chatbot
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create a `.env` file in the root directory
   - Add your Hugging Face API key:
     ```
     HF_API_KEY=your_hugging_face_api_key
     ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the chatbot**
   - Open your browser and go to `http://127.0.0.1:8000`

## Usage
- Start a conversation by entering your name, age, and reason for chat
- Engage with the chatbot by sharing your thoughts and feelings
- The chatbot will respond with empathy and ask follow-up questions

## Contributing
We welcome contributions to improve MindfulAI. Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
For questions or support, please contact [winnerbrown9@gmail.com].
