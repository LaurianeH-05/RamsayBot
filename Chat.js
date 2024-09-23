import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://127.0.0.1:5000/chat';

function Chat() {
    const [message, setMessage] = useState('');
    const [responses, setResponses] = useState([]); // Store multiple responses

    const sendMessage = async () => {
        if (!message) return; // Prevent sending empty messages

        try {
            const res = await axios.post(API_URL, { message });
            setResponses((prev) => [...prev, { type: 'user', text: message }, { type: 'bot', text: res.data.response }]);
            setMessage('');
        } catch (error) {
            console.error("Error sending message:", error);
            setResponses((prev) => [...prev, { type: 'bot', text: "An error occurred. Please try again." }]);
        }
    };

    return (
        <div className="chat-container">
            <div className="header">RAMSAYBOT</div>
            <div className="tips-banner">Tips: Format your questions as "recipe for", "substitution for", etc.</div>
            <div className="chat-box">
                {responses.map((msg, index) => (
                    <div key={index} className={msg.type === 'user' ? 'user-message' : 'bot-message'}>
                        {msg.text}
                    </div>
                ))}
            </div>
            <div className="input-banner">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message"
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}

export default Chat;
