import React, { useEffect, useState, useCallback } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/CyclicInventory.css';

const DAYS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

const CyclicInventory = () => {
    const [schedules, setSchedules] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [form, setForm] = useState({ name: '', weekday: 0, device_type: '' });
    const [msg, setMsg] = useState('');

    const headers = useCallback(() => ({
        Authorization: `Bearer ${authStore.getToken()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
    }), []);

    const load = useCallback(async () => {
        const [sRes, tRes] = await Promise.all([
            fetch('/api/cyclic-inventory/schedules', { headers: headers() }),
            fetch('/api/cyclic-inventory/tasks', { headers: headers() }),
        ]);
        if (sRes.ok) setSchedules((await sRes.json()).schedules || []);
        if (tRes.ok) setTasks((await tRes.json()).tasks || []);
    }, [headers]);

    useEffect(() => { load(); }, [load]);

    const createSchedule = async (e) => {
        e.preventDefault();
        await fetch('/api/cyclic-inventory/schedules', {
            method: 'POST', headers: headers(), body: JSON.stringify(form),
        });
        setForm({ name: '', weekday: 0, device_type: '' });
        load();
    };

    const generateToday = async () => {
        const res = await fetch('/api/cyclic-inventory/tasks/generate', { method: 'POST', headers: headers() });
        const d = await res.json();
        setMsg(`${d.created} tareas generadas`);
        load();
    };

    const complete = async (id) => {
        await fetch(`/api/cyclic-inventory/tasks/${id}/complete`, { method: 'POST', headers: headers(), body: '{}' });
        load();
    };

    return (
        <section className="cyclic-inv">
            <h1>Inventarios cíclicos</h1>
            <p>Programa conteos por día y categoría (ej. lunes = monitores).</p>

            <form onSubmit={createSchedule} className="ci-form">
                <input placeholder="Nombre (ej. Conteo monitores)" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                <select value={form.weekday} onChange={(e) => setForm({ ...form, weekday: parseInt(e.target.value, 10) })}>
                    {DAYS.map((d, i) => <option key={d} value={i}>{d}</option>)}
                </select>
                <input placeholder="Tipo dispositivo (opcional, ej. monitor)" value={form.device_type} onChange={(e) => setForm({ ...form, device_type: e.target.value })} />
                <button type="submit">Añadir programación</button>
            </form>

            <button type="button" className="ci-gen" onClick={generateToday}>Generar tareas de hoy</button>
            {msg && <p>{msg}</p>}

            <h2>Programaciones</h2>
            <ul>{schedules.map((s) => <li key={s.id}>{DAYS[s.weekday]} — {s.name} {s.device_type ? `(${s.device_type})` : ''}</li>)}</ul>

            <h2>Tareas</h2>
            <ul className="ci-tasks">
                {tasks.map((t) => (
                    <li key={t.id}>
                        <span>{t.title} · {t.due_date} · {t.status}</span>
                        {t.status !== 'completada' && (
                            <button type="button" onClick={() => complete(t.id)}>Completar</button>
                        )}
                    </li>
                ))}
            </ul>
        </section>
    );
};

export default CyclicInventory;
