import React from 'react';

const ConsultInventory = () => {
    return (
        <section id="consultar">
            {/* <h1>Consultar Inventario</h1> */}
            <div style={{ overflowX: 'auto' }}>
                <table>
                    <thead>
                        {/* <tr>
                            <th>Barcode</th>
                            <th>Inventario</th>
                            <th>Dispositivo</th>
                            <th>Modelo</th>
                            <th>Cantidad</th>
                            <th>Acciones</th>
                        </tr> */}
                    </thead>
                    <tbody id="barcode-table-body">
                        {/* Rows will be added dynamically */}
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default ConsultInventory;
