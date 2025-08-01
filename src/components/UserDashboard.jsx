import React, { useState, useEffect } from 'react';
import { FaEdit, FaTrash, FaUserPlus, FaPlus } from 'react-icons/fa';
import authStore from '../services/AuthStore';
import { useNavigate } from 'react-router-dom';

const UserDashboard = () => {
    const navigate = useNavigate();
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
    const [deviceTypes, setDeviceTypes] = useState([]);
    const [editingType, setEditingType] = useState(null);
    const [showTypeModal, setShowTypeModal] = useState(false);
    const [typeForm, setTypeForm] = useState({ name: '' });
    const [typeError, setTypeError] = useState('');

    useEffect(() => {
        const checkAuthAndFetch = async () => {
            if (!authStore.isLoggedIn()) {
                console.log('No autenticado, redirigiendo a login');
                navigate('/login');
                return;
            }

            if (!authStore.isAdmin()) {
                console.log('Usuario no es admin, redirigiendo');
                navigate('/');
                return;
            }

            await fetchUsers();
            await fetchDeviceTypes();
        };

        checkAuthAndFetch();
    }, [navigate]);

    const fetchUsers = async () => {
        try {
            setIsLoading(true);
            setError('');
            
            const token = authStore.getToken();
            if (!token) {
                console.log('No token available, redirigiendo a login');
                navigate('/login');
                return;
            }
            
            console.log('Fetching users with token:', token);
            
            const response = await fetch('http://localhost:5000/api/users', {
                headers: {
                    'Authorization': token,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (response.status === 401) {
                console.log('Token expirado o inválido');
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            if (response.status === 403) {
                console.log('Usuario no autorizado');
                navigate('/');
                return;
            }

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || `Error ${response.status}: ${response.statusText}`);
            }

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

    const fetchDeviceTypes = async () => {
        try {
            setTypeError('');
            
            const token = authStore.getToken();
            if (!token) {
                navigate('/login');
                return;
            }
            
            const response = await fetch('http://localhost:5000/api/stock/types', {
                headers: {
                    'Authorization': token,
                    'Accept': 'application/json'
                }
            });

            if (response.status === 401) {
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Error al cargar tipos de dispositivos');
            }

            setDeviceTypes(data.types || []);
        } catch (error) {
            console.error('Error fetching device types:', error);
            setTypeError('Error al cargar tipos: ' + error.message);
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
        setError('');

        try {
            const token = authStore.getToken();
            if (!token) {
                navigate('/login');
                return;
            }

            const url = editingUser 
                ? `http://localhost:5000/api/users/${editingUser.id}`
                : 'http://localhost:5000/api/users';
            
            const method = editingUser ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Authorization': token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });

            if (response.status === 401) {
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Error al procesar usuario');
            }

            console.log('User operation successful:', data);
            setShowModal(false);
            setEditingUser(null);
            setFormData({
                username: '',
                password: '',
                user_type: 'usuario',
                is_active: true
            });
            await fetchUsers();
        } catch (error) {
            console.error('Error in handleSubmit:', error);
            setError('Error: ' + error.message);
        }
    };

    const handleTypeInputChange = (e) => {
        setTypeForm({ name: e.target.value });
    };

    const handleTypeSubmit = async (e) => {
        e.preventDefault();
        setTypeError('');

        try {
            const token = authStore.getToken();
            if (!token) {
                navigate('/login');
                return;
            }

            const url = editingType 
                ? `http://localhost:5000/api/stock/types/${editingType.id}`
                : 'http://localhost:5000/api/stock/types';
            
            const method = editingType ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Authorization': token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(typeForm)
            });

            if (response.status === 401) {
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Error al procesar tipo de dispositivo');
            }

            console.log('Type operation successful:', data);
            setShowTypeModal(false);
            setEditingType(null);
            setTypeForm({ name: '' });
            await fetchDeviceTypes();
        } catch (error) {
            console.error('Error in handleTypeSubmit:', error);
            setTypeError('Error: ' + error.message);
        }
    };

    const handleEdit = (user) => {
        setEditingUser(user);
        setFormData({
            username: user.username,
            password: '',
            user_type: user.user_type,
            is_active: user.is_active
        });
        setShowModal(true);
    };

    const handleDelete = async (userId) => {
        if (!window.confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
            return;
        }

        try {
            const token = authStore.getToken();
            if (!token) {
                navigate('/login');
                return;
            }

            const response = await fetch(`http://localhost:5000/api/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': token,
                    'Accept': 'application/json'
                },
                credentials: 'include'
            });

            if (response.status === 401) {
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Error al eliminar usuario');
            }

            console.log('User deleted successfully');
            await fetchUsers();
        } catch (error) {
            console.error('Error deleting user:', error);
            setError('Error al eliminar usuario: ' + error.message);
        }
    };

    const handleTypeEdit = (type) => {
        setEditingType(type);
        setTypeForm({ name: type.name });
        setShowTypeModal(true);
    };

    const handleTypeDelete = async (typeId) => {
        if (!window.confirm('¿Estás seguro de que quieres eliminar este tipo de dispositivo?')) {
            return;
        }

        try {
            const token = authStore.getToken();
            if (!token) {
                navigate('/login');
                return;
            }

            const response = await fetch(`http://localhost:5000/api/stock/types/${typeId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': token,
                    'Accept': 'application/json'
                },
                credentials: 'include'
            });

            if (response.status === 401) {
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Error al eliminar tipo de dispositivo');
            }

            console.log('Device type deleted successfully');
            await fetchDeviceTypes();
        } catch (error) {
            console.error('Error deleting device type:', error);
            setTypeError('Error al eliminar tipo: ' + error.message);
        }
    };

    const getCustomTypeId = (type) => {
        return type.id || `custom_${type.name}`;
    };

    if (isLoading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '200px',
                color: '#2d3436',
                fontSize: '18px'
            }}>
                Cargando panel de administración...
            </div>
        );
    }

    return (
        <div style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '20px',
            backgroundColor: '#f8f9fa',
            minHeight: '100vh'
        }}>
            {/* Users Section */}
            <div style={{
                backgroundColor: '#ffffff',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e9ecef',
                marginBottom: '24px',
                overflow: 'hidden'
            }}>
                <div style={{
                    background: '#6c5ce7',
                    color: '#ffffff',
                    padding: '20px',
                    borderBottom: '1px solid #e9ecef'
                }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <h2 style={{
                            margin: 0,
                            fontSize: '20px',
                            fontWeight: '600'
                        }}>
                            Gestión de Usuarios
                        </h2>
                        <button
                            onClick={() => {
                                setEditingUser(null);
                                setFormData({
                                    username: '',
                                    password: '',
                                    user_type: 'usuario',
                                    is_active: true
                                });
                                setShowModal(true);
                            }}
                            style={{
                                background: '#00b894',
                                color: '#ffffff',
                                border: 'none',
                                padding: '8px 16px',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '500',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                transition: 'background-color 0.3s ease'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = '#00a085'}
                            onMouseOut={(e) => e.target.style.backgroundColor = '#00b894'}
                        >
                            <FaUserPlus />
                            Agregar Usuario
                        </button>
                    </div>
                </div>

                {error && (
                    <div style={{
                        backgroundColor: 'rgba(225, 112, 85, 0.1)',
                        border: '1px solid #e17055',
                        color: '#e17055',
                        padding: '12px',
                        margin: '16px',
                        borderRadius: '8px',
                        fontSize: '14px'
                    }}>
                        {error}
                    </div>
                )}

                <div style={{ overflowX: 'auto' }}>
                    <table style={{
                        width: '100%',
                        borderCollapse: 'collapse',
                        backgroundColor: '#ffffff'
                    }}>
                        <thead style={{ backgroundColor: '#f8f9fa' }}>
                            <tr>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Usuario</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Tipo</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Estado</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id} style={{
                                    borderBottom: '1px solid #f1f2f6',
                                    transition: 'background-color 0.3s ease'
                                }}
                                onMouseOver={(e) => e.target.parentElement.style.backgroundColor = '#f8f9fa'}
                                onMouseOut={(e) => e.target.parentElement.style.backgroundColor = '#ffffff'}
                                >
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{user.username}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{user.user_type}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>
                                        <span style={{
                                            backgroundColor: user.is_active ? '#00b894' : '#e17055',
                                            color: '#ffffff',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            fontSize: '12px',
                                            fontWeight: '500'
                                        }}>
                                            {user.is_active ? 'Activo' : 'Inactivo'}
                                        </span>
                                    </td>
                                    <td style={{ padding: '15px' }}>
                                        <button
                                            onClick={() => handleEdit(user)}
                                            style={{
                                                background: '#74b9ff',
                                                color: '#ffffff',
                                                border: 'none',
                                                padding: '6px',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                marginRight: '8px',
                                                transition: 'background-color 0.3s ease'
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = '#0984e3'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = '#74b9ff'}
                                        >
                                            <FaEdit />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(user.id)}
                                            style={{
                                                background: '#fd79a8',
                                                color: '#ffffff',
                                                border: 'none',
                                                padding: '6px',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                transition: 'background-color 0.3s ease'
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = '#e84393'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = '#fd79a8'}
                                        >
                                            <FaTrash />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Device Types Section */}
            <div style={{
                backgroundColor: '#ffffff',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e9ecef',
                overflow: 'hidden'
            }}>
                <div style={{
                    background: '#a29bfe',
                    color: '#ffffff',
                    padding: '20px',
                    borderBottom: '1px solid #e9ecef'
                }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <h2 style={{
                            margin: 0,
                            fontSize: '20px',
                            fontWeight: '600'
                        }}>
                            Tipos de Dispositivos
                        </h2>
                        <button
                            onClick={() => {
                                setEditingType(null);
                                setTypeForm({ name: '' });
                                setShowTypeModal(true);
                            }}
                            style={{
                                background: '#fdcb6e',
                                color: '#2d3436',
                                border: 'none',
                                padding: '8px 16px',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '500',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                transition: 'background-color 0.3s ease'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = '#f39c12'}
                            onMouseOut={(e) => e.target.style.backgroundColor = '#fdcb6e'}
                        >
                            <FaPlus />
                            Agregar Tipo
                        </button>
                    </div>
                </div>

                {typeError && (
                    <div style={{
                        backgroundColor: 'rgba(225, 112, 85, 0.1)',
                        border: '1px solid #e17055',
                        color: '#e17055',
                        padding: '12px',
                        margin: '16px',
                        borderRadius: '8px',
                        fontSize: '14px'
                    }}>
                        {typeError}
                    </div>
                )}

                <div style={{ overflowX: 'auto' }}>
                    <table style={{
                        width: '100%',
                        borderCollapse: 'collapse',
                        backgroundColor: '#ffffff'
                    }}>
                        <thead style={{ backgroundColor: '#f8f9fa' }}>
                            <tr>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Nombre</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {deviceTypes.map(type => (
                                <tr key={getCustomTypeId(type)} style={{
                                    borderBottom: '1px solid #f1f2f6',
                                    transition: 'background-color 0.3s ease'
                                }}
                                onMouseOver={(e) => e.target.parentElement.style.backgroundColor = '#f8f9fa'}
                                onMouseOut={(e) => e.target.parentElement.style.backgroundColor = '#ffffff'}
                                >
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{type.name}</td>
                                    <td style={{ padding: '15px' }}>
                                        <button
                                            onClick={() => handleTypeEdit(type)}
                                            style={{
                                                background: '#74b9ff',
                                                color: '#ffffff',
                                                border: 'none',
                                                padding: '6px',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                marginRight: '8px',
                                                transition: 'background-color 0.3s ease'
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = '#0984e3'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = '#74b9ff'}
                                        >
                                            <FaEdit />
                                        </button>
                                        <button
                                            onClick={() => handleTypeDelete(type.id)}
                                            style={{
                                                background: '#fd79a8',
                                                color: '#ffffff',
                                                border: 'none',
                                                padding: '6px',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                transition: 'background-color 0.3s ease'
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = '#e84393'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = '#fd79a8'}
                                        >
                                            <FaTrash />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* User Modal */}
            {showModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        background: '#ffffff',
                        padding: '32px',
                        borderRadius: '12px',
                        boxShadow: '0 6px 12px rgba(0, 0, 0, 0.2)',
                        maxWidth: '500px',
                        width: '90%',
                        maxHeight: '80vh',
                        overflowY: 'auto'
                    }}>
                        <h3 style={{
                            margin: '0 0 24px 0',
                            color: '#2d3436',
                            fontSize: '18px',
                            fontWeight: '600'
                        }}>
                            {editingUser ? 'Editar Usuario' : 'Agregar Usuario'}
                        </h3>

                        <form onSubmit={handleSubmit}>
                            <div style={{ marginBottom: '20px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    color: '#2d3436',
                                    fontWeight: '500',
                                    fontSize: '14px'
                                }}>
                                    Usuario:
                                </label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        border: '2px solid #dfe6e9',
                                        borderRadius: '8px',
                                        fontSize: '14px',
                                        outline: 'none',
                                        transition: 'border-color 0.3s ease',
                                        boxSizing: 'border-box'
                                    }}
                                    onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                                    onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                                />
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    color: '#2d3436',
                                    fontWeight: '500',
                                    fontSize: '14px'
                                }}>
                                    Contraseña:
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    required={!editingUser}
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        border: '2px solid #dfe6e9',
                                        borderRadius: '8px',
                                        fontSize: '14px',
                                        outline: 'none',
                                        transition: 'border-color 0.3s ease',
                                        boxSizing: 'border-box'
                                    }}
                                    onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                                    onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                                />
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    color: '#2d3436',
                                    fontWeight: '500',
                                    fontSize: '14px'
                                }}>
                                    Tipo de Usuario:
                                </label>
                                <select
                                    name="user_type"
                                    value={formData.user_type}
                                    onChange={handleInputChange}
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        border: '2px solid #dfe6e9',
                                        borderRadius: '8px',
                                        fontSize: '14px',
                                        outline: 'none',
                                        transition: 'border-color 0.3s ease',
                                        backgroundColor: '#ffffff',
                                        color: '#2d3436'
                                    }}
                                    onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                                    onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                                >
                                    <option value="usuario">Usuario</option>
                                    <option value="admin">Administrador</option>
                                </select>
                            </div>

                            <div style={{ marginBottom: '24px' }}>
                                <label style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    color: '#2d3436',
                                    fontWeight: '500',
                                    fontSize: '14px',
                                    cursor: 'pointer'
                                }}>
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active}
                                        onChange={handleInputChange}
                                        style={{
                                            marginRight: '8px',
                                            transform: 'scale(1.2)'
                                        }}
                                    />
                                    Usuario Activo
                                </label>
                            </div>

                            <div style={{
                                display: 'flex',
                                gap: '12px',
                                justifyContent: 'flex-end'
                            }}>
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    style={{
                                        background: '#636e72',
                                        color: '#ffffff',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontSize: '14px',
                                        fontWeight: '500',
                                        transition: 'background-color 0.3s ease'
                                    }}
                                    onMouseOver={(e) => e.target.style.backgroundColor = '#4a4a4a'}
                                    onMouseOut={(e) => e.target.style.backgroundColor = '#636e72'}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    style={{
                                        background: '#00b894',
                                        color: '#ffffff',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontSize: '14px',
                                        fontWeight: '500',
                                        transition: 'background-color 0.3s ease'
                                    }}
                                    onMouseOver={(e) => e.target.style.backgroundColor = '#00a085'}
                                    onMouseOut={(e) => e.target.style.backgroundColor = '#00b894'}
                                >
                                    {editingUser ? 'Actualizar' : 'Crear'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Type Modal */}
            {showTypeModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        background: '#ffffff',
                        padding: '32px',
                        borderRadius: '12px',
                        boxShadow: '0 6px 12px rgba(0, 0, 0, 0.2)',
                        maxWidth: '400px',
                        width: '90%'
                    }}>
                        <h3 style={{
                            margin: '0 0 24px 0',
                            color: '#2d3436',
                            fontSize: '18px',
                            fontWeight: '600'
                        }}>
                            {editingType ? 'Editar Tipo' : 'Agregar Tipo de Dispositivo'}
                        </h3>

                        <form onSubmit={handleTypeSubmit}>
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    color: '#2d3436',
                                    fontWeight: '500',
                                    fontSize: '14px'
                                }}>
                                    Nombre del Tipo:
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    value={typeForm.name}
                                    onChange={handleTypeInputChange}
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        border: '2px solid #dfe6e9',
                                        borderRadius: '8px',
                                        fontSize: '14px',
                                        outline: 'none',
                                        transition: 'border-color 0.3s ease',
                                        boxSizing: 'border-box'
                                    }}
                                    onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                                    onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                                />
                            </div>

                            <div style={{
                                display: 'flex',
                                gap: '12px',
                                justifyContent: 'flex-end'
                            }}>
                                <button
                                    type="button"
                                    onClick={() => setShowTypeModal(false)}
                                    style={{
                                        background: '#636e72',
                                        color: '#ffffff',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontSize: '14px',
                                        fontWeight: '500',
                                        transition: 'background-color 0.3s ease'
                                    }}
                                    onMouseOver={(e) => e.target.style.backgroundColor = '#4a4a4a'}
                                    onMouseOut={(e) => e.target.style.backgroundColor = '#636e72'}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    style={{
                                        background: '#fdcb6e',
                                        color: '#2d3436',
                                        border: 'none',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontSize: '14px',
                                        fontWeight: '500',
                                        transition: 'background-color 0.3s ease'
                                    }}
                                    onMouseOver={(e) => e.target.style.backgroundColor = '#f39c12'}
                                    onMouseOut={(e) => e.target.style.backgroundColor = '#fdcb6e'}
                                >
                                    {editingType ? 'Actualizar' : 'Crear'}
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