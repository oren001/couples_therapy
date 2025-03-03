'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { FaMicrophone, FaStop, FaPaperPlane, FaCheck, FaArrowLeft } from 'react-icons/fa';

// Define types
interface Message {
  role: 'user' | 'assistant' | 'therapist';
  content: string;
  approved?: boolean;
}

export default function Partner2Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Start recording audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        sendAudioToAPI(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Error accessing microphone. Please check your permissions.');
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop all tracks on the stream
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  // Send audio to API
  const sendAudioToAPI = async (audioBlob: Blob) => {
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      
      const response = await axios.post('http://localhost:8000/partner/2/audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Add user message (we don't know what was said, but we'll get it from the API response)
      const transcribedText = response.data.transcribed_text || "Audio message";
      setMessages(prev => [...prev, { role: 'user', content: transcribedText }]);
      
      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.text }]);
      
      // Play audio response
      if (response.data.audio_base64) {
        const audio = `data:audio/mp3;base64,${response.data.audio_base64}`;
        setAudioUrl(audio);
        if (audioRef.current) {
          audioRef.current.src = audio;
          audioRef.current.play();
        }
      }
    } catch (error) {
      console.error('Error sending audio:', error);
      alert('Error communicating with your representor. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Send text message
  const sendTextMessage = async () => {
    if (!inputText.trim()) return;
    
    const userMessage = inputText;
    setInputText('');
    setIsLoading(true);
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    
    try {
      const response = await axios.post('http://localhost:8000/partner/2/text', {
        text: userMessage,
        partner_id: 2
      });
      
      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.text }]);
      
      // Play audio response
      if (response.data.audio_base64) {
        const audio = `data:audio/mp3;base64,${response.data.audio_base64}`;
        setAudioUrl(audio);
        if (audioRef.current) {
          audioRef.current.src = audio;
          audioRef.current.play();
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error communicating with your representor. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Approve message to send to therapist
  const approveMessageToTherapist = async (message: Message, index: number) => {
    if (message.role !== 'assistant') return;
    
    setIsLoading(true);
    
    try {
      const response = await axios.post('http://localhost:8000/partner/2/approve', {
        text: message.content,
        partner_id: 2
      });
      
      // Mark message as approved
      const updatedMessages = [...messages];
      updatedMessages[index] = { ...message, approved: true };
      setMessages(updatedMessages);
      
      // Add therapist response
      setMessages(prev => [...prev, { role: 'therapist', content: response.data.text }]);
      
      // Play audio response
      if (response.data.audio_base64) {
        const audio = `data:audio/mp3;base64,${response.data.audio_base64}`;
        setAudioUrl(audio);
        if (audioRef.current) {
          audioRef.current.src = audio;
          audioRef.current.play();
        }
      }
    } catch (error) {
      console.error('Error approving message:', error);
      alert('Error communicating with the therapist. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-purple-600 text-white p-4 flex items-center">
        <Link href="/" className="mr-4">
          <FaArrowLeft />
        </Link>
        <h1 className="text-xl font-bold">Partner 2 - Therapy Session</h1>
      </header>
      
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">
            <p className="text-lg mb-2">Welcome to your therapy session</p>
            <p>Start by speaking or typing a message to your representor</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`p-3 rounded-lg max-w-[80%] ${
                message.role === 'user' 
                  ? 'bg-purple-100 ml-auto' 
                  : message.role === 'assistant'
                    ? 'bg-white border border-gray-200'
                    : 'bg-blue-100'
              }`}
            >
              <div className="font-semibold text-xs text-gray-500 mb-1">
                {message.role === 'user' ? 'You' : message.role === 'assistant' ? 'Your Representor' : 'Therapist'}
              </div>
              <p>{message.content}</p>
              
              {/* Approve button for assistant messages */}
              {message.role === 'assistant' && !message.approved && (
                <button 
                  onClick={() => approveMessageToTherapist(message, index)}
                  className="mt-2 text-xs bg-green-500 text-white px-2 py-1 rounded flex items-center gap-1"
                  disabled={isLoading}
                >
                  <FaCheck size={10} /> Share with Therapist
                </button>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex items-center gap-2">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-3 rounded-full ${
              isRecording ? 'bg-red-500 text-white' : 'bg-purple-500 text-white'
            }`}
            disabled={isLoading}
          >
            {isRecording ? <FaStop /> : <FaMicrophone />}
          </button>
          
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
            placeholder="Type a message..."
            className="flex-1 p-2 border border-gray-300 rounded-lg"
            disabled={isLoading || isRecording}
          />
          
          <button
            onClick={sendTextMessage}
            className="p-3 bg-purple-500 text-white rounded-full"
            disabled={isLoading || !inputText.trim() || isRecording}
          >
            <FaPaperPlane />
          </button>
        </div>
        
        {isLoading && (
          <div className="text-center text-sm text-gray-500 mt-2">
            Processing...
          </div>
        )}
      </div>
      
      {/* Hidden audio element for playing responses */}
      <audio ref={audioRef} className="hidden" controls />
    </div>
  );
} 