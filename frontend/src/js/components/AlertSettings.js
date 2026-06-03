import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/AlertSettings.css';

const CHANNELS = ['email', 'telegram', 'discord'];
const EVENTS = ['low_stock', 'critical_stock', 'expiring_soon', 'order_approved'];

const AlertSettings = () => {
    const [configs, setConfigs] = useState([]);
    const [form, setForm] = useState({
        channel: 'email', event_type: 'low_stock', destination: '', enabled: true,
        extra_config: { bot_token: '' },
    });
    const [message, setMessage] = useState('');

    const headers = useCallback(() => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    }), []);

    const load = useCallback(async () => {
        const res = await fetch('/api/alerts', { headers: headers() });
        if (res.ok) {
            const d = await res.json();
            setConfigs(d.configs || []);
        }
    }, [headers]);

    useEffect(() => { load(); }, [load]);

    const save = async (e) => {
        e.preventDefault();
        await fetch('/api/alerts', {
            method: 'PUT',
            headers: headers(),
            body: JSON.stringify(form),
        });
        setMessage('Configuración guardada');
        load();
    };

    const runCheck = async () => {
        const res = await fetch('/api/alerts/check', { method: 'POST', headers: headers() });
        const d = await res.json();
        setMessage(`Revisión: ${d.critical_count} críticos, ${d.low_count} bajos`);
    };

    const testAlert = async () => {
        await fetch('/api/alerts/test', {
            method: 'POST',
            headers: headers(),
            body: JSON.stringify({ event_type: form.event_type, message: 'Prueba de alerta' }),
        });
        setMessage('Alerta de prueba enviada (si hay canal configurado)');
    };

    return (
        <section className="alert-settings">
            <h1>Alertas automáticas</h1>
            <p>Email, Telegram y Discord para stock bajo, crítico y órdenes aprobadas.</p>

            <form onSubmit={save} className="alert-form">
                <select value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}>
                    {CHANNELS.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
                <select value={form.event_type} onChange={(e) => setForm({ ...form, event_type: e.target.value })}>
                    {EVENTS.map((ev) => <option key={ev} value={ev}>{ev}</option>)}
                </select>
                <input
                    placeholder="Destino (email / chat_id / webhook URL)"
                    value={form.destination}
                    onChange={(e) => setForm({ ...form, destination: e.target.value })}
                />
                {form.channel === 'telegram' && (
                    <input
                        placeholder="Bot token (Telegram)"
                        value={form.extra_config.bot_token}
                        onChange={(e) => setForm({ ...form, extra_config: { bot_token: e.target.value } })}
                    />
                )}
                <label><input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} /> Activo</label>
                <button type="submit">Guardar</button>
            </form>

            <div className="alert-actions">
                <button type="button" onClick={runCheck}>Revisar stock ahora</button>
                <button type="button" onClick={testAlert}>Enviar prueba</button>
            </div>

            {message && <p className="alert-msg">{message}</p>}

            <h2>Canales configurados</h2>
            <ul>
                {configs.map((c) => (
                    <li key={c.id}>{c.channel} · {c.event_type} · {c.destination || '—'} · {c.enabled ? '✓' : '✗'}</li>
                ))}
            </ul>
        </section>
    );
};

export default AlertSettings;
