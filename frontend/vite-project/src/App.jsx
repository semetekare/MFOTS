import './App.css'
import { useNavigate } from 'react-router-dom';

function App() {
    const navigate = useNavigate();

    return (
        <div className="container">
            <div className="traffic_small">
                <img src="/traffic_small_RYG.png" alt="traffic_small"/>
            </div>
            <div>
                <h1>Изучение различных подходов к определению метрик формирования очередей транспортных средств</h1>
                <button onClick={() => navigate('/Model_traffic_light')}>Просмотр</button>
            </div>
        </div>
    );
}

export default App;
