import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import MetarView from './Metar/MetarView';
import reportWebVitals from './reportWebVitals';

// index.js or App.js
async function fetchConfig() {
  try {
    const response = await fetch('/config.json');
    const config = await response.json();
    window.REACT_APP_API_URL = config.apiUrl; // Store in global variable
    renderApp(); // Render your react App after fetching the config.
  } catch (error) {
    console.error('Error fetching config:', error);
    // Handle error (e.g., default URL)
    window.REACT_APP_API_URL = "http://localhost:5000/v1/api";
    renderApp();
  }
}

function renderApp(){
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <MetarView />
    </React.StrictMode>
  );
}

fetchConfig();
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
