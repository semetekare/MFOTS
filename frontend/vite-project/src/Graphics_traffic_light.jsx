import React from "react";
import { Link } from "react-router-dom";
import "./Graphics_traffic_light.css";

function GraphicsTrafficLight() {
    return (
        <div className="app-container">
            <aside className="sidebar">
                <div className="logo">
                    <img src="/icon_traffic_light.png" alt="Smart traffic light" />
                    <p>Smart Traffic Light</p>
                </div>
                <nav className="menu">
                    <Link to="/">Главная</Link>
                    <Link to="/Graphics_traffic_light">Отчет</Link>
                    <Link to="/Model_traffic_light">Симуляция</Link>
                    <Link to="/about">О нас</Link>
                </nav>
            </aside>
            <main className="simulation-container expanded">
                <div className="intersection">
                    <p>Тут будет график</p>
                </div>
            </main>
        </div>
    );
}

export default GraphicsTrafficLight;