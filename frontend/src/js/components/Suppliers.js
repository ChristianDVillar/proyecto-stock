import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Suppliers.css';

const emptyForm = { name: '', tax_id: '', phone: '', email: '', address: '', notes: '' };

const Suppliers = () => {
    const [suppliers, setSuppliers] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const headers = () => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    });

    const load = useCallback(async () => {
        const res = await fetch('/api/suppliers', { headers: headers() });
        if (res.ok) {
            const data = await res.json();
            setSuppliers(data.suppliers || []);
        }
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        const res = await fetch('/api/suppliers', {
            method: 'POST',
            headers: headers(),
            body: JSON.stringify(form),
        });
        if (res.ok) {
            setForm(emptyForm);
            setMessage('Proveedor creado');
            load();
        } else {
            const d = await res.json().catch(() => ({}));
            setError(d.error || 'Error al crear');
        }
    };

    return (
        <section className="suppliers-page">
            <h1>Gestión de proveedores</h1>

            <form className="supplier-form" onSubmit={handleSubmit}>
                <h2>Nuevo proveedor</h2>
                <div className="form-row">
                    <input placeholder="Nombre *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                    <input placeholder="CIF/NIF" value={form.tax_id} onChange={(e) => setForm({ ...form, tax_id: e.target.value })} />
                </div>
                <div className="form-row">
                    <input placeholder="Teléfono" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                    <input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                </div>
                <input placeholder="Dirección" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                <textarea placeholder="Notas" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} />
                <button type="submit">Guardar proveedor</button>
                {message && <p className="msg-ok">{message}</p>}
                {error && <p className="msg-err">{error}</p>}
            </form>

            <div className="suppliers-list">
                <h2>Proveedores activos ({suppliers.length})</h2>
                <table>
                    <thead>
                        <tr><th>Nombre</th><th>CIF/NIF</th><th>Teléfono</th><th>Email</th></tr>
                    </thead>
                    <tbody>
                        {suppliers.map((s) => (
                            <tr key={s.id}>
                                <td>{s.name}</td>
                                <td>{s.tax_id || '—'}</td>
                                <td>{s.phone || '—'}</td>
                                <td>{s.email || '—'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default Suppliers;
