import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './index.css';
import App from './App.jsx';
import ModelTrafficLight from './Model_traffic_light.jsx'; // Добавляем компонент

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<App />} />
                <Route path="/Model_traffic_light" element={<ModelTrafficLight />} />
            </Routes>
        </BrowserRouter>
    </StrictMode>
);
