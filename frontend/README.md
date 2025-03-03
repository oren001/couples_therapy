# Couples Therapy LLM System - Frontend

This is the frontend for the Couples Therapy LLM System, which uses OpenAI's GPT-4 Turbo, Whisper, and TTS APIs to create a voice-enabled couples therapy experience.

## Overview

The Couples Therapy LLM System creates an innovative approach to couples therapy using three interconnected LLMs:

1. **Central Therapist LLM (Mediator)**: Acts as the professional therapist, guiding the overall conversation and therapy process with therapeutic expertise.

2. **Partner Representor LLMs (2)**: Each partner has their own dedicated LLM that serves as their "representative" in the therapy process, helping them formulate thoughts constructively.

## Features

- **Voice Interaction**: Speak directly to your representor LLM using your microphone.
- **Text Messaging**: Type messages to your representor LLM.
- **Audio Responses**: Hear responses from your representor through text-to-speech.
- **Therapist Mediation**: Share approved messages with the therapist LLM for mediation.
- **Constructive Communication**: Representor LLMs help refine thoughts into constructive language.

## Getting Started

1. Make sure the backend server is running first:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   python run.py
   ```

2. Then, run the frontend development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) with your browser.

4. Click on either "Partner 1" or "Partner 2" to start your therapy session.

## Communication Flow

1. Partner speaks or types a message to their Representor LLM.
2. Representor LLM helps refine the message and responds.
3. Partner approves the refined message to share with the Therapist LLM.
4. Therapist LLM mediates and responds.
5. Representor LLM interprets the therapist's response for the partner.

## Technologies Used

- **Next.js**: React framework for the frontend.
- **Tailwind CSS**: For styling the application.
- **Axios**: For API requests to the backend.
- **React Icons**: For UI icons.
- **Web Audio API**: For recording and processing audio.

## Project Structure

- `src/app/page.tsx`: Main landing page with links to partner interfaces.
- `src/app/partner/1/page.tsx`: Partner 1's interface.
- `src/app/partner/2/page.tsx`: Partner 2's interface.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
