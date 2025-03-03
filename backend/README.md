# Couples Therapy LLM System - Backend

This is the backend for the Couples Therapy LLM System, which uses OpenAI's GPT-4 Turbo, Whisper, and TTS APIs to create a voice-enabled couples therapy experience.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Run the server:
   ```
   python run.py
   ```

## API Endpoints

- `POST /partner/{partner_id}/audio`: Process audio from a partner
- `POST /partner/{partner_id}/text`: Process text from a partner
- `POST /partner/{partner_id}/approve`: Approve a message to be sent to the therapist

## Architecture

The system consists of three LLMs:
1. Therapist LLM: Acts as the professional therapist
2. Partner 1 Representor LLM: Helps Partner 1 formulate thoughts
3. Partner 2 Representor LLM: Helps Partner 2 formulate thoughts

The communication flow is:
1. Partner → Representor LLM
2. Representor LLM → Therapist LLM (after partner approval)
3. Therapist LLM → Representor LLM
4. Representor LLM → Partner 