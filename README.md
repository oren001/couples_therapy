# Couples Therapy AI Assistant

An interactive couples therapy application that uses AI to help partners communicate more effectively.

## Features
- Real-time AI-powered responses using GPT-3.5-turbo and GPT-4
- Interactive interface for both partners
- AI therapist providing professional guidance
- Secure and private conversations

## Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/couples-therapy-llm.git
cd couples-therapy-llm
```

2. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create a `.env` file in the `backend` directory with the following:
```
OPENAI_API_KEY=your_openai_api_key_here
PARTNER_MODEL=gpt-3.5-turbo
THERAPIST_MODEL=gpt-4
PORT=8000
HOST=127.0.0.1
DEBUG=True
```
Replace `your_openai_api_key_here` with your actual OpenAI API key from https://platform.openai.com/account/api-keys

4. **Start the Server**
```bash
cd backend
python server.py
```

5. **Open the Application**
Open `frontend/simple-test.html` in your web browser to use the simple interface, or
Open `frontend/advanced-test.html` for the full three-panel interface.

## Usage Guide

1. **Check Connection**
- Click "Check Status" to verify the server is running and API is configured

2. **Start a Conversation**
- Choose which partner you want to be (Partner 1 or 2)
- Type your message in the text box
- Click "Send" to get AI suggestions for better communication
- Click "Approve" if you like the suggestion to get the therapist's perspective

3. **Debug Information**
- Click "Show Debug Info" to see detailed API responses and server logs

## Security Note
This is a development version for testing purposes. For production use:
- Use HTTPS
- Implement proper authentication
- Add data encryption
- Host on a secure server

## Support
For issues or questions, please open an issue in the repository.

## License
[Your chosen license] 