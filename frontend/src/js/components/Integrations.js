import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Integrations.css';

const Integrations = () => {
    const [keys, setKeys] = useState([]);
    const [webhooks, setWebhooks] = useState([]);
    const [newKey, setNewKey] = useState('');
    const [whUrl, setWhUrl] = useState('');

    const headers = useCallback(() => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    }), []);

    const load = useCallback(async () => {
        const [kRes, wRes] = await Promise.all([
            fetch('/api/integrations/api-keys', { headers: headers() }),
            fetch('/api/integrations/webhooks', { headers: headers() }),
        ]);
        if (kRes.ok) setKeys((await kRes.json()).api_keys || []);
        if (wRes.ok) setWebhooks((await wRes.json()).webhooks || []);
    }, [headers]);

    useEffect(() => { load(); }, [load]);

    const createKey = async () => {
        const res = await fetch('/api/integrations/api-keys', {
            method: 'POST', headers: headers(), body: JSON.stringify({ name: 'Integración' }),
        });
        if (res.ok) {
            const d = await res.json();
            setNewKey(d.key);
            load();
        }
    };

    const createWebhook = async () => {
        if (!whUrl) return;
        await fetch('/api/integrations/webhooks', {
            method: 'POST', headers: headers(), body: JSON.stringify({ url: whUrl }),
        });
        setWhUrl('');
        load();
    };

    return (
        <section className="integrations-page">
            <h1>API pública e integraciones</h1>
            <p>Conecta Shopify, WooCommerce, TPV u otros sistemas vía API key y webhooks.</p>

            <h2>API Keys</h2>
            <button type="button" onClick={createKey}>Generar API key</button>
            {newKey && (
                <p className="key-once">Copia ahora (solo se muestra una vez): <code>{newKey}</code></p>
            )}
            <ul>{keys.map((k) => <li key={k.id}>{k.name} · {k.key_prefix}… · {k.scopes}</li>)}</ul>
            <p className="hint">Header: <code>X-API-Key: sk_…</code> · Base: <code>/api/v1/stock</code></p>

            <h2>Webhooks</h2>
            <div className="wh-row">
                <input placeholder="https://tu-servidor.com/webhook" value={whUrl} onChange={(e) => setWhUrl(e.target.value)} />
                <button type="button" onClick={createWebhook}>Añadir</button>
            </div>
            <ul>{webhooks.map((w) => <li key={w.id}>{w.url} · {w.events}</li>)}</ul>
        </section>
    );
};

export default Integrations;
