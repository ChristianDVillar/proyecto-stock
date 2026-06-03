import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/BillingPlans.css';

const BillingPlans = () => {
    const [plans, setPlans] = useState([]);
    const [usage, setUsage] = useState(null);
    const [msg, setMsg] = useState('');

    const headers = useCallback(() => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    }), []);

    useEffect(() => {
        Promise.all([
            fetch('/api/billing/plans', { headers: headers() }),
            fetch('/api/billing/usage', { headers: headers() }),
        ]).then(async ([pRes, uRes]) => {
            if (pRes.ok) setPlans((await pRes.json()).plans || []);
            if (uRes.ok) setUsage(await uRes.json());
        });
    }, [headers]);

    const selectPlan = async (plan) => {
        const res = await fetch('/api/billing/plan', {
            method: 'PATCH', headers: headers(), body: JSON.stringify({ plan }),
        });
        if (res.ok) {
            setUsage(await res.json());
            setMsg(`Plan actualizado a ${plan}`);
        }
    };

    return (
        <section className="billing-plans">
            <h1>Planes SaaS</h1>
            {usage && (
                <div className="usage-box">
                    <p>Plan actual: <strong>{usage.plan}</strong></p>
                    <p>Usuarios: {usage.usage.users}{usage.limits.max_users ? ` / ${usage.limits.max_users}` : ''}</p>
                    <p>Almacenes: {usage.usage.warehouses}{usage.limits.max_warehouses ? ` / ${usage.limits.max_warehouses}` : ''}</p>
                    <p>Órdenes este mes: {usage.usage.orders_this_month}{usage.limits.max_orders_month ? ` / ${usage.limits.max_orders_month}` : ''}</p>
                </div>
            )}
            <div className="plan-grid">
                {plans.map((p) => (
                    <div key={p.plan} className={`plan-card ${usage?.plan === p.plan ? 'active' : ''}`}>
                        <h2>{p.label}</h2>
                        <p className="plan-price">{p.price_eur}€/mes</p>
                        <ul>
                            <li>{p.max_users ?? '∞'} usuarios</li>
                            <li>{p.max_warehouses ?? '∞'} almacenes</li>
                            <li>{p.max_orders_month ?? '∞'} órdenes/mes</li>
                        </ul>
                        <button type="button" onClick={() => selectPlan(p.plan)}>Seleccionar</button>
                    </div>
                ))}
            </div>
            {msg && <p className="billing-msg">{msg}</p>}
        </section>
    );
};

export default BillingPlans;
