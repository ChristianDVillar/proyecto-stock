import React, { useState, useRef, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/QuickScan.css';

const QuickScan = () => {
    const [scans, setScans] = useState([]);
    const [barcode, setBarcode] = useState('');
    const [mode, setMode] = useState('lookup');
    const [loading, setLoading] = useState(false);
    const inputRef = useRef(null);

    const headers = useCallback(() => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    }), []);

    const scan = async (code) => {
        const bc = (code || barcode).trim();
        if (!bc) return;
        setLoading(true);
        try {
            const res = await fetch('/api/stock/quick-scan', {
                method: 'POST',
                headers: headers(),
                body: JSON.stringify({ barcode: bc, mode, quantity: 1 }),
            });
            const data = await res.json();
            if (res.ok) {
                setScans((prev) => [{
                    id: Date.now(),
                    barcode: bc,
                    modelo: data.stock?.modelo,
                    cantidad: data.stock?.cantidad,
                    location_code: data.stock?.location_code,
                    mode,
                    time: new Date().toLocaleTimeString(),
                }, ...prev].slice(0, 50));
                setBarcode('');
                inputRef.current?.focus();
            } else {
                setScans((prev) => [{
                    id: Date.now(), barcode: bc, error: data.error, time: new Date().toLocaleTimeString(),
                }, ...prev].slice(0, 50));
            }
        } finally {
            setLoading(false);
        }
    };

    const onKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            scan();
        }
    };

    return (
        <section className="quick-scan-page">
            <h1>Inventario rápido</h1>
            <p className="qs-desc">Escanea códigos de barras sin abrir formularios. Ideal para móvil/PWA.</p>

            <div className="qs-controls">
                <select value={mode} onChange={(e) => setMode(e.target.value)}>
                    <option value="lookup">Solo consultar</option>
                    <option value="increment">Sumar +1</option>
                    <option value="decrement">Restar -1</option>
                </select>
                <input
                    ref={inputRef}
                    type="text"
                    placeholder="Escanear o escribir código..."
                    value={barcode}
                    onChange={(e) => setBarcode(e.target.value)}
                    onKeyDown={onKeyDown}
                    autoFocus
                    disabled={loading}
                />
                <button type="button" onClick={() => scan()} disabled={loading}>
                    {loading ? '…' : 'Escanear'}
                </button>
            </div>

            <ul className="qs-list">
                {scans.map((s) => (
                    <li key={s.id} className={s.error ? 'qs-error' : ''}>
                        <strong>{s.barcode}</strong>
                        {s.error ? (
                            <span>{s.error}</span>
                        ) : (
                            <span>{s.modelo} · qty {s.cantidad} · {s.location_code || '—'} · {s.time}</span>
                        )}
                    </li>
                ))}
            </ul>
        </section>
    );
};

export default QuickScan;
