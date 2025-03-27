import React from "react";
import { Link } from "react-router-dom";
import "./Model_traffic_light.css";

function ModelTrafficLight() {
    return (
        <div className="app-container">
            <aside className="sidebar">
                <div className="logo">
                    <img src="/icon_traffic_light.png" alt="Smart traffic light" />
                    <p>Smart Traffic Light</p>
                </div>
                <nav className="menu">
                    <Link to="/">Главная</Link>
                    <Link to="/report">Отчет</Link>
                    <Link to="/simulation">Симуляция</Link>
                    <Link to="/about">О нас</Link>
                </nav>
            </aside>
            <main className="simulation-container expanded">
                <div className="intersection">
                    <p>Тут будет симуляция...</p>
                </div>
            </main>
        </div>
    );
}

export default ModelTrafficLight;