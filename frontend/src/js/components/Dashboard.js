import React, { useEffect, useState } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Dashboard.css';

const levelLabel = (level) => {
    if (level === 'critico') return { text: 'Crítico', cls: 'level-critico' };
    if (level === 'bajo') return { text: 'Bajo', cls: 'level-bajo' };
    return { text: 'Normal', cls: 'level-normal' };
};

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const load = async () => {
            const token = authStore.getToken();
            if (!token) return;
            try {
                const res = await fetch('/api/dashboard/executive', {
                    headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
                });
                if (!res.ok) throw new Error('Error al cargar dashboard');
                setData(await res.json());
            } catch (e) {
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) return <div className="dashboard-loading">Cargando dashboard...</div>;
    if (error) return <div className="dashboard-error">{error}</div>;
    if (!data) return null;

    const { kpis, inventory_by_category, movements_summary, expiring_soon, critical_stock, warranty_alerts } = data;

    return (
        <section className="dashboard">
            <h1>Dashboard ejecutivo</h1>

            <div className="kpi-grid">
                <div className="kpi-card">
                    <span className="kpi-label">Valor inventario</span>
                    <span className="kpi-value">€{kpis.inventory_value.toLocaleString()}</span>
                </div>
                <div className="kpi-card">
                    <span className="kpi-label">Productos</span>
                    <span className="kpi-value">{kpis.total_items}</span>
                </div>
                <div className="kpi-card">
                    <span className="kpi-label">Unidades totales</span>
                    <span className="kpi-value">{kpis.total_units}</span>
                </div>
                <div className="kpi-card kpi-warn">
                    <span className="kpi-label">Stock crítico</span>
                    <span className="kpi-value">{kpis.critical_stock_count}</span>
                </div>
                <div className="kpi-card kpi-warn">
                    <span className="kpi-label">Próximos a vencer</span>
                    <span className="kpi-value">{kpis.expiring_soon_count}</span>
                </div>
                <div className="kpi-card">
                    <span className="kpi-label">Proveedores</span>
                    <span className="kpi-value">{kpis.suppliers_count}</span>
                </div>
            </div>

            <div className="dashboard-grid">
                <div className="dashboard-panel">
                    <h2>Inventario por categoría</h2>
                    <ul className="category-list">
                        {inventory_by_category.map((c) => (
                            <li key={c.category}>
                                <span className="cat-name">{c.category}</span>
                                <div className="cat-bar-wrap">
                                    <div className="cat-bar" style={{ width: `${c.percentage}%` }} />
                                </div>
                                <span className="cat-pct">{c.percentage}%</span>
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="dashboard-panel">
                    <h2>Movimientos (30 días)</h2>
                    <div className="movements-summary">
                        <div className="mov-item mov-in">
                            <span>Entradas</span>
                            <strong>{movements_summary.entradas}</strong>
                        </div>
                        <div className="mov-item mov-out">
                            <span>Salidas</span>
                            <strong>{movements_summary.salidas}</strong>
                        </div>
                    </div>
                </div>
            </div>

            <div className="dashboard-panel">
                <h2>Productos próximos a vencer</h2>
                {expiring_soon.length === 0 ? (
                    <p className="empty-msg">No hay productos próximos a vencer.</p>
                ) : (
                    <table className="dash-table">
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Lote</th>
                                <th>Días restantes</th>
                                <th>Alerta</th>
                            </tr>
                        </thead>
                        <tbody>
                            {expiring_soon.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.modelo} ({item.barcode})</td>
                                    <td>{item.batch_number || '—'}</td>
                                    <td>{item.days_until_expiration}</td>
                                    <td><span className={`alert-${item.alert_level}`}>{item.alert_level?.replace('_', ' ')}</span></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="dashboard-panel">
                <h2>Stock crítico (reposición)</h2>
                {critical_stock.length === 0 ? (
                    <p className="empty-msg">No hay productos en nivel crítico.</p>
                ) : (
                    <table className="dash-table">
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Actual</th>
                                <th>Mínimo</th>
                                <th>Óptimo</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {critical_stock.map((item) => {
                                const lvl = levelLabel(item.stock_level);
                                return (
                                    <tr key={item.id}>
                                        <td>{item.modelo}</td>
                                        <td>{item.cantidad}</td>
                                        <td>{item.minimum_stock}</td>
                                        <td>{item.optimal_stock ?? '—'}</td>
                                        <td><span className={lvl.cls}>{lvl.text}</span></td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            {warranty_alerts.length > 0 && (
                <div className="dashboard-panel">
                    <h2>Garantías próximas a expirar</h2>
                    <table className="dash-table">
                        <thead>
                            <tr><th>Activo</th><th>SN</th><th>Días restantes</th></tr>
                        </thead>
                        <tbody>
                            {warranty_alerts.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.modelo}</td>
                                    <td>{item.serial_number || '—'}</td>
                                    <td>{item.warranty_days} días</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </section>
    );
};

export default Dashboard;
