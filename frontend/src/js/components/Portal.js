import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Portal.css';

const Portal = () => {
    const [summary, setSummary] = useState(null);
    const [stock, setStock] = useState([]);
    const [q, setQ] = useState('');

    const headers = useCallback(() => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        Accept: 'application/json',
    }), []);

    useEffect(() => {
        fetch('/api/portal/summary', { headers: headers() })
            .then((r) => r.ok ? r.json() : null)
            .then(setSummary);
    }, [headers]);

    const search = async (e) => {
        e.preventDefault();
        const res = await fetch(`/api/portal/stock?q=${encodeURIComponent(q)}`, { headers: headers() });
        if (res.ok) setStock((await res.json()).items || []);
    };

    return (
        <section className="portal-page">
            <h1>Portal de cliente</h1>
            <p>Consulta stock y solicitudes sin acceso al panel administrativo.</p>
            {summary && (
                <div className="portal-kpis">
                    <span>Usuario: {summary.username}</span>
                    <span>Productos: {summary.stock_items}</span>
                    <span>Solicitudes pendientes: {summary.pending_requests}</span>
                </div>
            )}
            <form onSubmit={search} className="portal-search">
                <input placeholder="Buscar producto..." value={q} onChange={(e) => setQ(e.target.value)} />
                <button type="submit">Buscar</button>
            </form>
            <ul>
                {stock.map((s) => (
                    <li key={s.id}>{s.modelo} · {s.barcode} · qty {s.cantidad} · {s.location_code || '—'}</li>
                ))}
            </ul>
        </section>
    );
};

export default Portal;
