import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './assets/styles/base.css';
import './assets/styles/components.css';

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
