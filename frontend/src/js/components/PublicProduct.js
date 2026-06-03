import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import '../../styles/PublicProduct.css';

const PublicProduct = () => {
    const { token } = useParams();
    const [data, setData] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        fetch(`/api/public/product/${token}`)
            .then(async (r) => {
                if (!r.ok) throw new Error('Producto no disponible');
                return r.json();
            })
            .then(setData)
            .catch((e) => setError(e.message));
    }, [token]);

    if (error) return <div className="public-product"><p>{error}</p></div>;
    if (!data) return <div className="public-product"><p>Cargando…</p></div>;

    const p = data.product;
    return (
        <section className="public-product">
            <h1>{p.modelo}</h1>
            <p className="pp-barcode">{p.barcode}</p>
            {p.descripcion && <p>{p.descripcion}</p>}
            {p.location_code && <p><strong>Ubicación:</strong> {p.location_code}</p>}
            {p.warranty_days_remaining != null && (
                <p><strong>Garantía:</strong> {p.warranty_days_remaining} días restantes</p>
            )}
            {p.allergens?.length > 0 && (
                <p><strong>Alérgenos:</strong> {p.allergens.join(', ')}</p>
            )}
            {p.manual_pdf_url && (
                <a href={p.manual_pdf_url} target="_blank" rel="noreferrer">Descargar manual PDF</a>
            )}
            {data.maintenance?.length > 0 && (
                <>
                    <h2>Mantenimiento</h2>
                    <ul>{data.maintenance.map((m, i) => <li key={i}>{m.type} — {m.date}</li>)}</ul>
                </>
            )}
        </section>
    );
};

export default PublicProduct;
