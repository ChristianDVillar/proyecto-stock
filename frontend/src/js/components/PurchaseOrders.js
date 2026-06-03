import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/PurchaseOrders.css';

const statusLabel = {
    borrador: 'Borrador',
    pendiente: 'Pendiente',
    aprobada: 'Aprobada',
    recibida: 'Recibida',
    cancelada: 'Cancelada',
};

const PurchaseOrders = () => {
    const [orders, setOrders] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [supplierId, setSupplierId] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(null);

    const headers = () => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    });

    const loadOrders = useCallback(async () => {
        const res = await fetch('/api/purchase-orders', { headers: headers() });
        if (res.ok) {
            const data = await res.json();
            setOrders(data.purchase_orders || []);
        }
    }, []);

    const loadSuppliers = useCallback(async () => {
        const res = await fetch('/api/suppliers', { headers: headers() });
        if (res.ok) {
            const data = await res.json();
            setSuppliers(data.suppliers || []);
        }
    }, []);

    useEffect(() => {
        loadOrders();
        loadSuppliers();
    }, [loadOrders, loadSuppliers]);

    const generateFromLowStock = async () => {
        if (!supplierId) { setError('Selecciona un proveedor'); return; }
        setLoading('generate');
        setError('');
        setMessage('');
        const res = await fetch('/api/purchase-orders/generate-low-stock', {
            method: 'POST',
            headers: headers(),
            body: JSON.stringify({ supplier_id: parseInt(supplierId, 10) }),
        });
        setLoading(null);
        if (res.ok) {
            setMessage('Orden de compra generada desde stock bajo');
            loadOrders();
        } else {
            const d = await res.json().catch(() => ({}));
            setError(d.error || 'Error al generar');
        }
    };

    const approve = async (id) => {
        setLoading(id);
        const res = await fetch(`/api/purchase-orders/${id}/approve`, { method: 'POST', headers: headers() });
        setLoading(null);
        if (res.ok) { setMessage('Orden aprobada'); loadOrders(); }
        else { const d = await res.json().catch(() => ({})); setError(d.error); }
    };

    const receive = async (id) => {
        setLoading(id);
        const res = await fetch(`/api/purchase-orders/${id}/receive`, { method: 'POST', headers: headers() });
        setLoading(null);
        if (res.ok) { setMessage('Mercancía recibida — stock actualizado'); loadOrders(); }
        else { const d = await res.json().catch(() => ({})); setError(d.error); }
    };

    return (
        <section className="po-page">
            <h1>Órdenes de compra</h1>

            <div className="po-generate">
                <h2>Generar desde stock bajo</h2>
                <select value={supplierId} onChange={(e) => setSupplierId(e.target.value)}>
                    <option value="">Seleccionar proveedor</option>
                    {suppliers.map((s) => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                </select>
                <button onClick={generateFromLowStock} disabled={loading === 'generate'}>
                    {loading === 'generate' ? 'Generando...' : 'Generar OC'}
                </button>
            </div>

            {message && <p className="msg-ok">{message}</p>}
            {error && <p className="msg-err">{error}</p>}

            <div className="po-list">
                <h2>Órdenes ({orders.length})</h2>
                {orders.length === 0 ? (
                    <p className="empty">No hay órdenes de compra.</p>
                ) : (
                    orders.map((order) => (
                        <div key={order.id} className="po-card">
                            <div className="po-header">
                                <strong>{order.order_number}</strong>
                                <span className={`status status-${order.status}`}>{statusLabel[order.status] || order.status}</span>
                            </div>
                            <p>Proveedor: {order.supplier_name}</p>
                            <p>Total: €{(order.total_amount || 0).toFixed(2)}</p>
                            <ul className="po-lines">
                                {(order.lines || []).map((ln) => (
                                    <li key={ln.id}>{ln.description} — {ln.quantity_ordered} uds × €{(ln.unit_cost || 0).toFixed(2)}</li>
                                ))}
                            </ul>
                            <div className="po-actions">
                                {(order.status === 'borrador' || order.status === 'pendiente') && (
                                    <button onClick={() => approve(order.id)} disabled={loading === order.id}>Aprobar</button>
                                )}
                                {order.status === 'aprobada' && (
                                    <button onClick={() => receive(order.id)} disabled={loading === order.id}>Recibir mercancía</button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </section>
    );
};

export default PurchaseOrders;
