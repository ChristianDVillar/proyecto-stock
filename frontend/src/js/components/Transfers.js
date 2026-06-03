import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Transfers.css';

const Transfers = () => {
    const [transfers, setTransfers] = useState([]);
    const [warehouses, setWarehouses] = useState([]);
    const [stockOptions, setStockOptions] = useState([]);
    const [form, setForm] = useState({
        stock_id: '', from_warehouse_id: '', to_warehouse_id: '', quantity: '', notes: '',
    });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const headers = () => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    });

    const load = useCallback(async () => {
        const [tRes, wRes, sRes] = await Promise.all([
            fetch('/api/transfers', { headers: headers() }),
            fetch('/api/warehouses', { headers: headers() }),
            fetch('/api/stock/search?per_page=200', { headers: headers() }),
        ]);
        if (tRes.ok) { const d = await tRes.json(); setTransfers(d.transfers || []); }
        if (wRes.ok) { const d = await wRes.json(); setWarehouses(d.warehouses || []); }
        if (sRes.ok) { const d = await sRes.json(); setStockOptions(d.stocks || []); }
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const stock = stockOptions.find((s) => String(s.id) === String(form.stock_id));
        const res = await fetch('/api/transfers', {
            method: 'POST',
            headers: headers(),
            body: JSON.stringify({
                ...form,
                stock_id: parseInt(form.stock_id, 10),
                from_warehouse_id: parseInt(form.from_warehouse_id, 10),
                to_warehouse_id: parseInt(form.to_warehouse_id, 10),
                quantity: stock ? stock.cantidad : parseInt(form.quantity, 10),
            }),
        });
        if (res.ok) {
            setMessage('Transferencia creada (pendiente de completar)');
            setForm({ stock_id: '', from_warehouse_id: '', to_warehouse_id: '', quantity: '', notes: '' });
            load();
        } else {
            const d = await res.json().catch(() => ({}));
            setError(d.error || 'Error');
        }
    };

    const complete = async (id) => {
        const res = await fetch(`/api/transfers/${id}/complete`, { method: 'POST', headers: headers() });
        if (res.ok) { setMessage('Transferencia completada'); load(); }
        else { const d = await res.json().catch(() => ({})); setError(d.error); }
    };

    return (
        <section className="transfers-page">
            <h1>Transferencias entre almacenes</h1>

            <form className="tr-form" onSubmit={handleSubmit}>
                <select value={form.stock_id} onChange={(e) => setForm({ ...form, stock_id: e.target.value })} required>
                    <option value="">Producto</option>
                    {stockOptions.map((s) => (
                        <option key={s.id} value={s.id}>{s.modelo} ({s.barcode}) — {s.cantidad} uds</option>
                    ))}
                </select>
                <select value={form.from_warehouse_id} onChange={(e) => setForm({ ...form, from_warehouse_id: e.target.value })} required>
                    <option value="">Almacén origen</option>
                    {warehouses.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
                </select>
                <select value={form.to_warehouse_id} onChange={(e) => setForm({ ...form, to_warehouse_id: e.target.value })} required>
                    <option value="">Almacén destino</option>
                    {warehouses.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
                </select>
                <input placeholder="Notas" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
                <button type="submit">Solicitar transferencia</button>
            </form>

            {message && <p className="msg-ok">{message}</p>}
            {error && <p className="msg-err">{error}</p>}

            <div className="tr-list">
                <h2>Historial</h2>
                {transfers.map((t) => (
                    <div key={t.id} className="tr-card">
                        <strong>{t.stock_barcode}</strong>: {t.from_warehouse_name} → {t.to_warehouse_name}
                        <span className={`tr-status tr-${t.status}`}>{t.status}</span>
                        {t.status === 'pendiente' && (
                            <button type="button" onClick={() => complete(t.id)}>Completar</button>
                        )}
                    </div>
                ))}
            </div>
        </section>
    );
};

export default Transfers;
