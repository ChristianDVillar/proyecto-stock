import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Warehouses.css';

const Warehouses = () => {
    const [warehouses, setWarehouses] = useState([]);
    const [form, setForm] = useState({ code: '', name: '', city: '', address: '' });
    const [selectedStock, setSelectedStock] = useState(null);
    const [message, setMessage] = useState('');

    const headers = () => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    });

    const load = useCallback(() => {
        fetch('/api/warehouses', { headers: headers() })
            .then((r) => r.ok ? r.json() : { warehouses: [] })
            .then((d) => setWarehouses(d.warehouses || []));
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const res = await fetch('/api/warehouses', {
            method: 'POST',
            headers: headers(),
            body: JSON.stringify(form),
        });
        if (res.ok) {
            setForm({ code: '', name: '', city: '', address: '' });
            setMessage('Almacén creado');
            load();
        }
    };

    const viewStock = async (id) => {
        const res = await fetch(`/api/warehouses/${id}/stock`, { headers: headers() });
        if (res.ok) setSelectedStock(await res.json());
    };

    return (
        <section className="warehouses-page">
            <h1>Multi-almacén</h1>

            <form className="wh-form" onSubmit={handleSubmit}>
                <h2>Nuevo almacén</h2>
                <div className="wh-row">
                    <input placeholder="Código (ej. MAD)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required />
                    <input placeholder="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div className="wh-row">
                    <input placeholder="Ciudad" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
                    <input placeholder="Dirección" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                </div>
                <button type="submit">Crear almacén</button>
                {message && <p className="msg-ok">{message}</p>}
            </form>

            <div className="wh-list">
                <h2>Almacenes ({warehouses.length})</h2>
                <table>
                    <thead>
                        <tr><th>Código</th><th>Nombre</th><th>Ciudad</th><th>Default</th><th></th></tr>
                    </thead>
                    <tbody>
                        {warehouses.map((w) => (
                            <tr key={w.id}>
                                <td>{w.code}</td>
                                <td>{w.name}</td>
                                <td>{w.city || '—'}</td>
                                <td>{w.is_default ? '✓' : ''}</td>
                                <td><button type="button" onClick={() => viewStock(w.id)}>Ver stock</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {selectedStock && (
                <div className="wh-stock-panel">
                    <h3>Stock en {selectedStock.warehouse.name} ({selectedStock.total})</h3>
                    <button type="button" onClick={() => setSelectedStock(null)}>Cerrar</button>
                    <ul>
                        {selectedStock.items.map((item) => (
                            <li key={item.id}>{item.modelo} — {item.barcode} ({item.cantidad})</li>
                        ))}
                    </ul>
                </div>
            )}
        </section>
    );
};

export default Warehouses;
