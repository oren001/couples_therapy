"use client";

import { useState, useEffect } from 'react';

export default function Home() {
  const [partner1Message, setPartner1Message] = useState('');
  const [partner2Message, setPartner2Message] = useState('');
  const [partner1Response, setPartner1Response] = useState('');
  const [partner2Response, setPartner2Response] = useState('');
  const [therapistResponse, setTherapistResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [activePartner, setActivePartner] = useState(null);
  const [showHowItWorks, setShowHowItWorks] = useState(false);
  const [apiStatus, setApiStatus] = useState('Checking...');

  // Check if the API is running
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/test');
        const data = await response.json();
        if (data.status === "API is working correctly") {
          setApiStatus('Connected');
        } else {
          setApiStatus('Error connecting to API');
        }
      } catch (error) {
        setApiStatus('API not available');
      }
    };

    checkApiStatus();
  }, []);

  const handlePartnerSubmit = async (partnerId, message) => {
    if (!message.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/partner/${partnerId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      const data = await response.json();
      
      if (partnerId === 1) {
        setPartner1Response(data.response);
      } else {
        setPartner2Response(data.response);
      }
    } catch (error) {
      console.error('Error:', error);
      if (partnerId === 1) {
        setPartner1Response('Error: Could not get response from the server.');
      } else {
        setPartner2Response('Error: Could not get response from the server.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApproveMessage = async (partnerId, message) => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/partner/${partnerId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      const data = await response.json();
      setTherapistResponse(data.response);
    } catch (error) {
      console.error('Error:', error);
      setTherapistResponse('Error: Could not get response from the therapist.');
    } finally {
      setLoading(false);
    }
  };

  // If no partner is selected, show the landing page
  if (activePartner === null) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
        <div className="max-w-6xl mx-auto p-8">
          <header className="mb-12 flex justify-between items-center">
            <h1 className="text-4xl font-bold text-indigo-900">Couples Therapy Assistant</h1>
            <span className={`px-3 py-1 rounded-full text-sm ${
              apiStatus === 'Connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              API Status: {apiStatus}
            </span>
          </header>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            <div 
              className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-indigo-300"
              onClick={() => setActivePartner(1)}
            >
              <h2 className="text-2xl font-bold text-indigo-800 mb-4">Partner 1 →</h2>
              <p className="text-gray-700 mb-6">Access your personal representor LLM to help express your thoughts and feelings.</p>
              <button 
                className="bg-indigo-600 text-white py-2 px-6 rounded-md hover:bg-indigo-700 transition-colors"
                onClick={() => setActivePartner(1)}
              >
                Start Session
              </button>
            </div>

            <div 
              className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-indigo-300"
              onClick={() => setActivePartner(2)}
            >
              <h2 className="text-2xl font-bold text-indigo-800 mb-4">Partner 2 →</h2>
              <p className="text-gray-700 mb-6">Access your personal representor LLM to help express your thoughts and feelings.</p>
              <button 
                className="bg-indigo-600 text-white py-2 px-6 rounded-md hover:bg-indigo-700 transition-colors"
                onClick={() => setActivePartner(2)}
              >
                Start Session
              </button>
            </div>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-lg mb-12">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-indigo-800">How It Works</h2>
              <button 
                className="text-indigo-600 hover:text-indigo-800"
                onClick={() => setShowHowItWorks(!showHowItWorks)}
              >
                {showHowItWorks ? 'Hide Details' : 'Show Details'}
              </button>
            </div>
            
            {showHowItWorks ? (
              <ol className="list-decimal pl-6 space-y-4 text-gray-700">
                <li>Each partner communicates privately with their Representor LLM</li>
                <li>The Representor helps refine thoughts and suggests constructive phrasing</li>
                <li>Once approved by the partner, the Representor shares this with the Therapist LLM</li>
                <li>The Therapist LLM mediates between both sides, guiding toward resolution</li>
                <li>Communication flows back to the partners through their respective Representors</li>
              </ol>
            ) : (
              <p className="text-gray-700">
                Our AI-powered couples therapy assistant helps partners communicate more effectively by providing 
                personalized guidance and mediation. Click "Show Details" to learn more about the process.
              </p>
            )}
          </div>

          <footer className="text-center text-gray-600 text-sm">
            <p>© 2023 Couples Therapy Assistant. All rights reserved.</p>
          </footer>
        </div>
      </main>
    );
  }

  // If a partner is selected, show the chat interface
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto p-8">
        <header className="mb-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button 
              className="text-indigo-600 hover:text-indigo-800 font-medium"
              onClick={() => setActivePartner(null)}
            >
              ← Back to Home
            </button>
            <h1 className="text-3xl font-bold text-indigo-900">
              Partner {activePartner} Session
            </h1>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm ${
            apiStatus === 'Connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            API Status: {apiStatus}
          </span>
        </header>

        <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
          <h2 className="text-xl font-semibold mb-4 text-indigo-800">Your Message</h2>
          <div className="mb-4">
            <textarea
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows="5"
              value={activePartner === 1 ? partner1Message : partner2Message}
              onChange={(e) => activePartner === 1 
                ? setPartner1Message(e.target.value) 
                : setPartner2Message(e.target.value)
              }
              placeholder="Express your thoughts and feelings here..."
            ></textarea>
          </div>
          <button
            className="bg-indigo-600 text-white py-2 px-6 rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
            onClick={() => handlePartnerSubmit(activePartner, activePartner === 1 ? partner1Message : partner2Message)}
            disabled={loading || !(activePartner === 1 ? partner1Message.trim() : partner2Message.trim())}
          >
            {loading ? 'Sending...' : 'Get Suggestions'}
          </button>
        </div>

        {/* Representor Response */}
        {((activePartner === 1 && partner1Response) || (activePartner === 2 && partner2Response)) && (
          <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
            <h2 className="text-xl font-semibold mb-4 text-indigo-800">Suggested Improvement</h2>
            <div className="p-5 bg-indigo-50 rounded-lg mb-4 text-gray-800">
              <p>{activePartner === 1 ? partner1Response : partner2Response}</p>
            </div>
            <button
              className="bg-green-600 text-white py-2 px-6 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
              onClick={() => handleApproveMessage(
                activePartner, 
                activePartner === 1 ? partner1Response : partner2Response
              )}
              disabled={loading}
            >
              Approve & Send to Therapist
            </button>
          </div>
        )}

        {/* Therapist Response */}
        {therapistResponse && (
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-indigo-800">Therapist Response</h2>
            <div className="p-5 bg-yellow-50 rounded-lg text-gray-800">
              <p>{therapistResponse}</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
} 