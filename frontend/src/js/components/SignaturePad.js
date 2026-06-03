import React, { useRef, useEffect } from 'react';

/**
 * Canvas de firma digital (sin dependencias externas).
 */
const SignaturePad = ({ onSave, disabled }) => {
    const canvasRef = useRef(null);
    const drawing = useRef(false);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = '#222';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
    }, []);

    const pos = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return { x: clientX - rect.left, y: clientY - rect.top };
    };

    const start = (e) => {
        if (disabled) return;
        e.preventDefault();
        drawing.current = true;
        const { x, y } = pos(e);
        const ctx = canvasRef.current.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(x, y);
    };

    const move = (e) => {
        if (!drawing.current || disabled) return;
        e.preventDefault();
        const { x, y } = pos(e);
        const ctx = canvasRef.current.getContext('2d');
        ctx.lineTo(x, y);
        ctx.stroke();
    };

    const end = () => { drawing.current = false; };

    const clear = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    const save = () => {
        if (onSave) onSave(canvasRef.current.toDataURL('image/png'));
    };

    return (
        <div className="signature-pad">
            <canvas
                ref={canvasRef}
                width={400}
                height={150}
                style={{ border: '1px solid #ccc', borderRadius: 4, touchAction: 'none', maxWidth: '100%' }}
                onMouseDown={start}
                onMouseMove={move}
                onMouseUp={end}
                onMouseLeave={end}
                onTouchStart={start}
                onTouchMove={move}
                onTouchEnd={end}
            />
            <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                <button type="button" onClick={clear} disabled={disabled}>Limpiar</button>
                <button type="button" onClick={save} disabled={disabled}>Confirmar firma</button>
            </div>
        </div>
    );
};

export default SignaturePad;
