import React, { useState, useEffect } from 'react';
import '../../styles/SolicitarElementos.css';
import authStore from '../../stores/AuthStore';
import SignaturePad from './SignaturePad';

const SolicitarElementos = () => {
    const [formData, setFormData] = useState({
        request_date: new Date().toISOString().split('T')[0],
        duration_type: 'semanas',
        duration_value: 1,
        signed: false,
        stock_id: ''
    });
    const [solicitudes, setSolicitudes] = useState([]);
    const [stockOptions, setStockOptions] = useState([]);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [actionLoading, setActionLoading] = useState(null); // id de solicitud en proceso
    const [signatureData, setSignatureData] = useState(null);

    const userName = authStore.getUserName();
    const isAdmin = authStore.isAdmin();

    useEffect(() => {
        fetchSolicitudes();
    }, []);

    useEffect(() => {
        if (!isAdmin) {
            const token = authStore.getToken();
            if (!token) return;
            fetch('/api/stock/search?per_page=200', {
                headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/json' }
            })
                .then(res => res.ok ? res.json() : { stocks: [] })
                .then(data => setStockOptions(data.stocks || []))
                .catch(() => setStockOptions([]));
        }
    }, [isAdmin]);

    const fetchSolicitudes = async () => {
        const token = authStore.getToken();
        if (!token) return;
        try {
            const res = await fetch('/api/solicitudes', {
                headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/json' }
            });
            if (res.ok) {
                const data = await res.json();
                setSolicitudes(data.solicitudes || []);
            }
        } catch (_) {}
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        const token = authStore.getToken();
        if (!token) {
            setError('Debe iniciar sesión.');
            return;
        }
        if (!formData.signed && !signatureData) {
            setError('Debe firmar la solicitud (casilla o firma digital).');
            return;
        }
        const payload = {
            request_date: formData.request_date,
            duration_type: formData.duration_type,
            signed: true,
        };
        if (signatureData) payload.signature_data = signatureData;
        if (formData.stock_id) {
            const sid = parseInt(formData.stock_id, 10);
            if (!isNaN(sid)) payload.stock_id = sid;
        }
        if (formData.duration_type !== 'definitivo') {
            const val = parseInt(formData.duration_value, 10);
            if (isNaN(val) || val <= 0) {
                setError('Indique un valor válido (semanas u horas).');
                return;
            }
            payload.duration_value = val;
        }
        setLoading(true);
        try {
            const res = await fetch('/api/solicitudes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                setError(data.message || data.error || 'Error al enviar la solicitud.');
                return;
            }
            setMessage('Solicitud registrada correctamente.');
            setFormData(prev => ({
                ...prev,
                request_date: new Date().toISOString().split('T')[0],
                duration_value: 1,
                signed: false,
                stock_id: ''
            }));
            setSignatureData(null);
            fetchSolicitudes();
        } catch (err) {
            setError('Error de conexión.');
        } finally {
            setLoading(false);
        }
    };

    const handleAdminAction = async (reqId, status, deliveryDate) => {
        const token = authStore.getToken();
        if (!token) return;
        setActionLoading(reqId);
        try {
            const body = { status };
            if (deliveryDate) body.delivery_date = deliveryDate;
            const res = await fetch(`/api/solicitudes/${reqId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify(body)
            });
            if (res.ok) fetchSolicitudes();
        } finally {
            setActionLoading(null);
        }
    };

    const formatStockLabel = (s) => {
        if (!s) return '-';
        const parts = [s.inventario || s.barcode, s.dispositivo, s.modelo].filter(Boolean);
        return parts.length ? parts.join(' · ') : `#${s.id}`;
    };

    return (
        <div className="solicitar-elementos">
            <h2>Solicitar elementos</h2>
            <p className="solicitar-desc">Complete el formulario para registrar una solicitud. El tiempo puede ser en semanas, horas o definitivo.</p>

            <form onSubmit={handleSubmit} className="solicitar-form">
                <div className="form-group">
                    <label>Usuario</label>
                    <input type="text" value={userName || ''} readOnly className="form-control readonly" />
                </div>
                {!isAdmin && (
                    <div className="form-group">
                        <label htmlFor="stock_id">Elemento solicitado</label>
                        <select
                            id="stock_id"
                            name="stock_id"
                            value={formData.stock_id}
                            onChange={handleChange}
                            className="form-control"
                        >
                            <option value="">— Seleccionar elemento (opcional) —</option>
                            {stockOptions.map(s => (
                                <option key={s.id} value={s.id}>
                                    {formatStockLabel(s)}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
                <div className="form-group">
                    <label htmlFor="request_date">Fecha de solicitud</label>
                    <input
                        type="date"
                        id="request_date"
                        name="request_date"
                        value={formData.request_date}
                        onChange={handleChange}
                        className="form-control"
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="duration_type">Tiempo de solicitud</label>
                    <select
                        id="duration_type"
                        name="duration_type"
                        value={formData.duration_type}
                        onChange={handleChange}
                        className="form-control"
                    >
                        <option value="semanas">Semanas</option>
                        <option value="horas">Horas</option>
                        <option value="definitivo">Definitivo</option>
                    </select>
                </div>
                {formData.duration_type !== 'definitivo' && (
                    <div className="form-group">
                        <label htmlFor="duration_value">
                            {formData.duration_type === 'semanas' ? 'Número de semanas' : 'Número de horas'}
                        </label>
                        <input
                            type="number"
                            id="duration_value"
                            name="duration_value"
                            min="1"
                            value={formData.duration_value}
                            onChange={handleChange}
                            className="form-control"
                        />
                    </div>
                )}
                <div className="form-group">
                    <label>Firma digital (opcional)</label>
                    <SignaturePad onSave={(data) => { setSignatureData(data); setFormData(p => ({ ...p, signed: true })); }} disabled={loading} />
                    {signatureData && <p className="success-message">Firma capturada</p>}
                </div>
                <div className="form-group form-group-checkbox">
                    <label>
                        <input
                            type="checkbox"
                            name="signed"
                            checked={formData.signed}
                            onChange={handleChange}
                        />
                        <span>Firmo la solicitud</span>
                    </label>
                </div>
                {error && <div className="error-message">{error}</div>}
                {message && <div className="success-message">{message}</div>}
                <button type="submit" className="submit-btn" disabled={loading}>
                    {loading ? 'Enviando…' : 'Enviar solicitud'}
                </button>
            </form>

            {solicitudes.length > 0 && (
                <div className="solicitudes-list">
                    <h3>{isAdmin ? 'Todas las solicitudes' : 'Mis solicitudes'}</h3>
                    <table className="solicitudes-table">
                        <thead>
                            <tr>
                                {isAdmin && <th>Usuario</th>}
                                {isAdmin && <th>Elemento</th>}
                                <th>Fecha solicitud</th>
                                <th>Tiempo</th>
                                <th>Firmada</th>
                                <th>Estado</th>
                                <th>Fecha entrega</th>
                                {isAdmin && <th>Acciones</th>}
                                {!isAdmin && <th>Fecha registro</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {solicitudes.map(s => (
                                <tr key={s.id}>
                                    {isAdmin && <td>{s.request_username || '-'}</td>}
                                    {isAdmin && <td>{formatStockLabel(s.stock)}</td>}
                                    <td>{s.request_date}</td>
                                    <td>
                                        {s.duration_type === 'definitivo'
                                            ? 'Definitivo'
                                            : `${s.duration_value} ${s.duration_type}`}
                                    </td>
                                    <td>{s.signed ? 'Sí' : 'No'}</td>
                                    <td>{s.status || 'pendiente'}</td>
                                    <td>{s.delivery_date || '-'}</td>
                                    {isAdmin && (
                                        <td className="solicitudes-actions">
                                            {(s.status || 'pendiente') === 'pendiente' && (
                                                <>
                                                    <input
                                                        type="date"
                                                        className="solicitud-delivery-input"
                                                        id={`delivery-${s.id}`}
                                                        min={new Date().toISOString().split('T')[0]}
                                                    />
                                                    <button
                                                        type="button"
                                                        className="btn-approve"
                                                        disabled={actionLoading === s.id}
                                                        onClick={() => {
                                                            const input = document.getElementById(`delivery-${s.id}`);
                                                            handleAdminAction(s.id, 'aprobado', input?.value || null);
                                                        }}
                                                    >
                                                        Aprobar
                                                    </button>
                                                    <button
                                                        type="button"
                                                        className="btn-reject"
                                                        disabled={actionLoading === s.id}
                                                        onClick={() => handleAdminAction(s.id, 'rechazado')}
                                                    >
                                                        Rechazar
                                                    </button>
                                                </>
                                            )}
                                            {actionLoading === s.id && <span className="action-loading">...</span>}
                                        </td>
                                    )}
                                    {!isAdmin && (
                                        <td>{s.created_at ? new Date(s.created_at).toLocaleString() : '-'}</td>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default SolicitarElementos;
