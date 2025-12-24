/**
 * Stocker Mobile App
 * React Native application for inventory management
 */

import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  FlatList,
} from 'react-native';

interface StockItem {
  id: number;
  barcode: string;
  inventario: string;
  dispositivo: string;
  modelo: string;
  cantidad: number;
  status: string;
  location: string;
}

interface User {
  username: string;
  user_type: string;
}

const API_BASE_URL = 'http://localhost:5000/api';

const App = (): JSX.Element => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [stocks, setStocks] = useState<StockItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentView, setCurrentView] = useState<'login' | 'inventory' | 'search'>('login');

  useEffect(() => {
    // Check for stored token
    // In a real app, use AsyncStorage or SecureStore
    const storedToken = null; // AsyncStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken);
      setIsLoggedIn(true);
      setCurrentView('inventory');
      loadInventory(storedToken);
    }
  }, []);

  const login = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Por favor ingrese usuario y contraseña');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        setToken(data.access_token);
        setUser(data.user);
        setIsLoggedIn(true);
        setCurrentView('inventory');
        loadInventory(data.access_token);
        Alert.alert('Éxito', 'Sesión iniciada correctamente');
      } else {
        Alert.alert('Error', data.error || 'Credenciales incorrectas');
      }
    } catch (error) {
      Alert.alert('Error', 'Error de conexión. Verifique que el servidor esté ejecutándose.');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsLoggedIn(false);
    setCurrentView('login');
    setStocks([]);
    setUsername('');
    setPassword('');
  };

  const loadInventory = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/stock/search?per_page=50`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStocks(data.stocks || []);
      } else if (response.status === 401) {
        logout();
        Alert.alert('Sesión expirada', 'Por favor inicie sesión nuevamente');
      }
    } catch (error) {
      console.error('Error loading inventory:', error);
      Alert.alert('Error', 'No se pudo cargar el inventario');
    }
  };

  const searchStocks = async () => {
    if (!token) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        q: searchQuery,
        per_page: 50,
      });

      const response = await fetch(`${API_BASE_URL}/stock/search?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStocks(data.stocks || []);
      }
    } catch (error) {
      console.error('Error searching stocks:', error);
      Alert.alert('Error', 'No se pudo realizar la búsqueda');
    } finally {
      setLoading(false);
    }
  };

  const renderStockItem = ({ item }: { item: StockItem }) => (
    <View style={styles.stockItem}>
      <Text style={styles.stockBarcode}>{item.barcode}</Text>
      <Text style={styles.stockInfo}>{item.inventario}</Text>
      <Text style={styles.stockInfo}>{item.dispositivo}</Text>
      <Text style={styles.stockInfo}>{item.modelo}</Text>
      <View style={styles.stockFooter}>
        <Text style={styles.stockQuantity}>Cantidad: {item.cantidad}</Text>
        <Text style={[styles.stockStatus, getStatusStyle(item.status)]}>
          {item.status}
        </Text>
      </View>
    </View>
  );

  const getStatusStyle = (status: string) => {
    const statusStyles: { [key: string]: object } = {
      disponible: { backgroundColor: '#c8e6c9', color: '#2e7d32' },
      en_uso: { backgroundColor: '#bbdefb', color: '#1565c0' },
      mantenimiento: { backgroundColor: '#ffe0b2', color: '#e65100' },
      baja: { backgroundColor: '#ffcdd2', color: '#c62828' },
    };
    return statusStyles[status] || { backgroundColor: '#f5f5f5', color: '#666' };
  };

  if (currentView === 'login') {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" />
        <View style={styles.loginContainer}>
          <Text style={styles.title}>Stocker Mobile</Text>
          <Text style={styles.subtitle}>Gestión de Inventario</Text>

          <TextInput
            style={styles.input}
            placeholder="Usuario"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
          />

          <TextInput
            style={styles.input}
            placeholder="Contraseña"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={login}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Iniciar Sesión</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.note}>
            Nota: Asegúrese de que el servidor esté ejecutándose en http://localhost:5000
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Inventario</Text>
        <TouchableOpacity onPress={logout} style={styles.logoutButton}>
          <Text style={styles.logoutText}>Salir</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Buscar por código, inventario, modelo..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={searchStocks}
        />
        <TouchableOpacity
          style={styles.searchButton}
          onPress={searchStocks}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.searchButtonText}>Buscar</Text>
          )}
        </TouchableOpacity>
      </View>

      {user && (
        <View style={styles.userInfo}>
          <Text style={styles.userText}>Usuario: {user.username}</Text>
          <Text style={styles.userText}>Tipo: {user.user_type}</Text>
        </View>
      )}

      <FlatList
        data={stocks}
        renderItem={renderStockItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No hay items en el inventario</Text>
          </View>
        }
        refreshing={loading}
        onRefresh={() => token && loadInventory(token)}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 40,
    color: '#666',
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 15,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  button: {
    height: 50,
    backgroundColor: '#4CAF50',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  note: {
    marginTop: 20,
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  logoutButton: {
    padding: 8,
  },
  logoutText: {
    color: '#f44336',
    fontSize: 16,
    fontWeight: '600',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  searchInput: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginRight: 10,
    backgroundColor: '#fff',
  },
  searchButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 80,
  },
  searchButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  userInfo: {
    padding: 10,
    backgroundColor: '#e3f2fd',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  userText: {
    fontSize: 14,
    color: '#1976D2',
  },
  listContainer: {
    padding: 10,
  },
  stockItem: {
    backgroundColor: '#fff',
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  stockBarcode: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  stockInfo: {
    fontSize: 14,
    color: '#666',
    marginBottom: 3,
  },
  stockFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  stockQuantity: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  stockStatus: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    overflow: 'hidden',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});

export default App;
