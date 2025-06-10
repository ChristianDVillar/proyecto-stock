import React, { useState, useEffect } from 'react';
import { FaEdit, FaTrash, FaUserPlus } from 'react-icons/fa';
import '../assets/styles/UserDashboard.css';
import authStore from '../services/AuthStore';

const UserDashboard = () => {
    const [users, setUsers] = useState([]);
    const [editingUser, setEditingUser] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        user_type: 'usuario',
        is_active: true
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkAuthAndFetch = async () => {
            if (!authStore.validateAuth()) {
                console.log('Auth validation failed');
                return;
            }

            if (!authStore.isAdmin()) {
                console.log('User is not admin');
                setError('Acceso no autorizado');
                return;
            }

            await fetchUsers();
        };

        checkAuthAndFetch();
    }, []);

    const fetchUsers = async () => {
        try {
            setIsLoading(true);
            setError('');
            
            const token = authStore.getToken();
            if (!token) {
                console.log('No token available');
                return;
            }
            
            console.log('Fetching users with token');
            
            const response = await fetch('http://localhost:5000/api/users', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            console.log('Response status:', response.status);
            
            if (response.status === 401 || response.status === 403) {
                const data = await response.json();
                setError(data.error || 'No autorizado');
                return;
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Non-JSON response:', text);
                throw new Error('El servidor no devolvió una respuesta JSON válida');
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Error al cargar usuarios');
            }

            const data = await response.json();
            console.log('Users data received:', data);
            setUsers(data.users || []);
            setError('');
        } catch (error) {
            console.error('Error in fetchUsers:', error);
            setError('Error al cargar usuarios: ' + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!authStore.validateAuth()) return;

        try {
            const token = authStore.getToken();
            const url = editingUser 
                ? `http://localhost:5000/api/users/${editingUser.id}`
                : 'http://localhost:5000/api/users';
            const method = editingUser ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Error en la operación');
            }

            await fetchUsers();
            setShowModal(false);
            setEditingUser(null);
            setFormData({
                username: '',
                password: '',
                user_type: 'usuario',
                is_active: true
            });
        } catch (error) {
            setError(error.message);
        }
    };

    const handleEdit = (user) => {
        if (!authStore.validateAuth()) return;
        
        setEditingUser(user);
        setFormData({
            username: user.username,
            user_type: user.user_type,
            is_active: user.is_active,
            password: ''
        });
        setShowModal(true);
    };

    const handleDelete = async (userId) => {
        if (!authStore.validateAuth()) return;
        
        if (!window.confirm('¿Está seguro de eliminar este usuario?')) return;

        try {
            const token = authStore.getToken();
            const response = await fetch(`http://localhost:5000/api/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Error al eliminar usuario');
            }
            
            await fetchUsers();
        } catch (error) {
            setError('Error al eliminar usuario: ' + error.message);
        }
    };

    return (
        <div className="user-dashboard">
            <h2>Gestión de Usuarios</h2>
            
            {error && <div className="error-message">{error}</div>}
            
            {isLoading ? (
                <div className="loading">Cargando usuarios...</div>
            ) : (
                <>
                    <button className="add-user-btn" onClick={() => {
                        setEditingUser(null);
                        setFormData({
                            username: '',
                            password: '',
                            user_type: 'usuario',
                            is_active: true
                        });
                        setShowModal(true);
                    }}>
                        <FaUserPlus /> Nuevo Usuario
                    </button>

                    <div className="users-table-container">
                        <table className="users-table">
                            <thead>
                                <tr>
                                    <th>Usuario</th>
                                    <th>Tipo</th>
                                    <th>Estado</th>
                                    <th>Fecha Creación</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr key={user.id}>
                                        <td>{user.username}</td>
                                        <td>{user.user_type}</td>
                                        <td>{user.is_active ? 'Activo' : 'Inactivo'}</td>
                                        <td>{new Date(user.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <button className="edit-btn" onClick={() => handleEdit(user)}>
                                                <FaEdit />
                                            </button>
                                            <button className="delete-btn" onClick={() => handleDelete(user.id)}>
                                                <FaTrash />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {showModal && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>{editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}</h3>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Usuario:</label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <label>Contraseña:</label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    required={!editingUser}
                                    placeholder={editingUser ? '(Dejar vacío para mantener)' : ''}
                                />
                            </div>
                            
                            <div className="form-group">
                                <label>Tipo de Usuario:</label>
                                <select
                                    name="user_type"
                                    value={formData.user_type}
                                    onChange={handleInputChange}
                                >
                                    <option value="usuario">Usuario</option>
                                    <option value="tecnico">Técnico</option>
                                    <option value="admin">Administrador</option>
                                </select>
                            </div>
                            
                            <div className="form-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active}
                                        onChange={handleInputChange}
                                    />
                                    Usuario Activo
                                </label>
                            </div>
                            
                            <div className="modal-buttons">
                                <button type="submit" className="save-btn">
                                    {editingUser ? 'Actualizar' : 'Crear'}
                                </button>
                                <button type="button" className="cancel-btn" onClick={() => setShowModal(false)}>
                                    Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserDashboard; 