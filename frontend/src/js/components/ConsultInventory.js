import React, { useState, useEffect } from 'react';
import { FaSearch, FaFilter, FaEye } from 'react-icons/fa';
import authStore from '../../stores/AuthStore';
import '../../styles/ConsultInventory.css';

const ConsultInventory = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        type: '',
        status: '',
        location: ''
    });
    const [showFilters, setShowFilters] = useState(false);
    const [stockTypes, setStockTypes] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [selectedStock, setSelectedStock] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    const itemsPerPage = 20;

    useEffect(() => {
        loadStockTypes();
        searchStocks();
    }, [currentPage, searchQuery, filters]);

    const loadStockTypes = async () => {
        try {
            const token = authStore.getToken();
            const response = await fetch('http://localhost:5000/api/stock/types', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setStockTypes(data.types || []);
            }
        } catch (err) {
            console.error('Error loading stock types:', err);
        }
    };

    const searchStocks = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = authStore.getToken();
            if (!token) {
                throw new Error('No hay sesión activa');
            }

            const params = new URLSearchParams({
                page: currentPage,
                per_page: itemsPerPage
            });

            if (searchQuery) {
                params.append('q', searchQuery);
            }
            if (filters.type) {
                params.append('type', filters.type);
            }
            if (filters.status) {
                params.append('status', filters.status);
            }
            if (filters.location) {
                params.append('location', filters.location);
            }

            const response = await fetch(`http://localhost:5000/api/stock/search?${params}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    authStore.logout();
                    return;
                }
                throw new Error('Error al buscar inventario');
            }

            const data = await response.json();
            setStocks(data.stocks || []);
            setTotalPages(data.total_pages || 1);
            setTotalItems(data.total_items || 0);
        } catch (err) {
            setError(err.message);
            console.error('Error searching stocks:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        setCurrentPage(1);
        searchStocks();
    };

    const handleFilterChange = (field, value) => {
        setFilters(prev => ({
            ...prev,
            [field]: value
        }));
        setCurrentPage(1);
    };

    const clearFilters = () => {
        setFilters({
            type: '',
            status: '',
            location: ''
        });
        setSearchQuery('');
        setCurrentPage(1);
    };

    const viewStockDetails = async (stockId) => {
        try {
            const token = authStore.getToken();
            const stock = stocks.find(s => s.id === stockId);
            if (!stock) return;

            const response = await fetch(`http://localhost:5000/api/stock/${stock.barcode}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setSelectedStock(data);
                setShowDetails(true);
            }
        } catch (err) {
            console.error('Error loading stock details:', err);
            alert('Error al cargar los detalles del stock');
        }
    };

    const getStatusBadgeClass = (status) => {
        const statusClasses = {
            'disponible': 'status-available',
            'en_uso': 'status-in-use',
            'mantenimiento': 'status-maintenance',
            'baja': 'status-low'
        };
        return statusClasses[status] || 'status-default';
    };

    return (
        <section id="consultar" className="consult-inventory">
            <h1>Consultar Inventario</h1>

            <div className="search-container">
                <form onSubmit={handleSearch} className="search-form">
                    <div className="search-input-group">
                        <FaSearch className="search-icon" />
                        <input
                            type="text"
                            placeholder="Buscar por código, inventario, dispositivo, modelo..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="search-input"
                        />
                        <button type="submit" className="search-button" disabled={loading}>
                            {loading ? 'Buscando...' : 'Buscar'}
                        </button>
                    </div>
                </form>

                <button
                    className="filter-toggle"
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <FaFilter /> {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
                </button>
            </div>

            {showFilters && (
                <div className="filters-panel">
                    <div className="filter-group">
                        <label>Tipo de Dispositivo:</label>
                        <select
                            value={filters.type}
                            onChange={(e) => handleFilterChange('type', e.target.value)}
                        >
                            <option value="">Todos</option>
                            {stockTypes.map(type => (
                                <option key={type.id} value={type.id}>
                                    {type.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Estado:</label>
                        <select
                            value={filters.status}
                            onChange={(e) => handleFilterChange('status', e.target.value)}
                        >
                            <option value="">Todos</option>
                            <option value="disponible">Disponible</option>
                            <option value="en_uso">En Uso</option>
                            <option value="mantenimiento">Mantenimiento</option>
                            <option value="baja">Baja</option>
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Ubicación:</label>
                        <input
                            type="text"
                            placeholder="Filtrar por ubicación"
                            value={filters.location}
                            onChange={(e) => handleFilterChange('location', e.target.value)}
                        />
                    </div>

                    <button className="clear-filters" onClick={clearFilters}>
                        Limpiar Filtros
                    </button>
                </div>
            )}

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            <div className="results-info">
                <p>
                    Mostrando {stocks.length} de {totalItems} resultados
                    {totalPages > 1 && ` (Página ${currentPage} de ${totalPages})`}
                </p>
            </div>

            {loading ? (
                <div className="loading">Cargando...</div>
            ) : stocks.length === 0 ? (
                <div className="no-results">
                    <p>No se encontraron resultados</p>
                </div>
            ) : (
                <>
                    <div className="table-container">
                        <table className="inventory-table">
                            <thead>
                                <tr>
                                    <th>Código de Barras</th>
                                    <th>Inventario</th>
                                    <th>Dispositivo</th>
                                    <th>Modelo</th>
                                    <th>Cantidad</th>
                                    <th>Estado</th>
                                    <th>Ubicación</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stocks.map((stock) => (
                                    <tr key={stock.id}>
                                        <td>{stock.barcode}</td>
                                        <td>{stock.inventario}</td>
                                        <td>{stock.dispositivo?.value || stock.dispositivo}</td>
                                        <td>{stock.modelo}</td>
                                        <td>{stock.cantidad}</td>
                                        <td>
                                            <span className={`status-badge ${getStatusBadgeClass(stock.status)}`}>
                                                {stock.status}
                                            </span>
                                        </td>
                                        <td>{stock.location || 'N/A'}</td>
                                        <td>
                                            <button
                                                className="action-button view-button"
                                                onClick={() => viewStockDetails(stock.id)}
                                                title="Ver detalles"
                                            >
                                                <FaEye />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {totalPages > 1 && (
                        <div className="pagination">
                            <button
                                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                disabled={currentPage === 1}
                                className="page-button"
                            >
                                Anterior
                            </button>
                            <span className="page-info">
                                Página {currentPage} de {totalPages}
                            </span>
                            <button
                                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                disabled={currentPage === totalPages}
                                className="page-button"
                            >
                                Siguiente
                            </button>
                        </div>
                    )}
                </>
            )}

            {showDetails && selectedStock && (
                <div className="modal-overlay" onClick={() => setShowDetails(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Detalles del Stock</h2>
                            <button className="close-button" onClick={() => setShowDetails(false)}>
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="detail-section">
                                <h3>Información General</h3>
                                <div className="detail-grid">
                                    <div className="detail-item">
                                        <label>Código de Barras:</label>
                                        <span>{selectedStock.stock.barcode}</span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Inventario:</label>
                                        <span>{selectedStock.stock.inventario}</span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Dispositivo:</label>
                                        <span>{selectedStock.stock.dispositivo}</span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Modelo:</label>
                                        <span>{selectedStock.stock.modelo}</span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Descripción:</label>
                                        <span>{selectedStock.stock.descripcion || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Cantidad:</label>
                                        <span>{selectedStock.stock.cantidad}</span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Estado:</label>
                                        <span className={`status-badge ${getStatusBadgeClass(selectedStock.stock.status)}`}>
                                            {selectedStock.stock.status}
                                        </span>
                                    </div>
                                    <div className="detail-item">
                                        <label>Ubicación:</label>
                                        <span>{selectedStock.stock.location || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>

                            {selectedStock.movements && selectedStock.movements.length > 0 && (
                                <div className="detail-section">
                                    <h3>Últimos Movimientos</h3>
                                    <table className="movements-table">
                                        <thead>
                                            <tr>
                                                <th>Tipo</th>
                                                <th>Cantidad</th>
                                                <th>Fecha</th>
                                                <th>Notas</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {selectedStock.movements.map((movement, idx) => (
                                                <tr key={idx}>
                                                    <td>{movement.type}</td>
                                                    <td>{movement.quantity}</td>
                                                    <td>{new Date(movement.timestamp).toLocaleString()}</td>
                                                    <td>{movement.notes || 'N/A'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {selectedStock.last_maintenance && (
                                <div className="detail-section">
                                    <h3>Último Mantenimiento</h3>
                                    <div className="detail-grid">
                                        <div className="detail-item">
                                            <label>Tipo:</label>
                                            <span>{selectedStock.last_maintenance.type}</span>
                                        </div>
                                        <div className="detail-item">
                                            <label>Fecha:</label>
                                            <span>{new Date(selectedStock.last_maintenance.date).toLocaleDateString()}</span>
                                        </div>
                                        <div className="detail-item">
                                            <label>Estado:</label>
                                            <span>{selectedStock.last_maintenance.status}</span>
                                        </div>
                                        <div className="detail-item">
                                            <label>Descripción:</label>
                                            <span>{selectedStock.last_maintenance.description || 'N/A'}</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
};

export default ConsultInventory;
