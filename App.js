import React from 'react';
import './App.css';
import Chat from './Chat'; // Import the Chat component

function App() {
    return (
        <div className="App">
            <h1>Chat with RamsayBot</h1>
            <Chat /> {/* Add the Chat component here */}
        </div>
    );
}

export default App;
