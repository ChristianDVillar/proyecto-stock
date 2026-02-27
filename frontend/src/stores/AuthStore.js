// AuthStore.js
import { EventEmitter } from 'events';

const AUTH_DEBUG = false; // set true to see auth/session logs

class AuthStore extends EventEmitter {
    constructor() {
        super();
        this._isInitialized = false;
        this._token = null;
        this._userName = '';
        this._userType = '';
        this._isLoggedIn = false;
        
        // Inicializar inmediatamente desde localStorage
        this.initializeFromStorage();
        
        // Agregar listener para cambios en localStorage
        window.addEventListener('storage', this.handleStorageChange.bind(this));
        
        // Verificar el token periódicamente
        this.startTokenVerification();
    }

    startTokenVerification() {
        // Verificar el token cada 5 minutos
        setInterval(async () => {
            if (this._token) {
                await this.verifyToken();
            }
        }, 5 * 60 * 1000);
    }

    handleStorageChange(event) {
        if (AUTH_DEBUG) console.log('Storage change detected:', event);
        if (event.key === 'jwt_token' || event.key === 'username' || event.key === 'user_type') {
            this.initializeFromStorage();
        }
    }

    async initializeFromStorage() {
        try {
            // Get all auth data from storage
            const token = localStorage.getItem('jwt_token');
            const username = localStorage.getItem('username');
            const userType = localStorage.getItem('user_type');

            if (AUTH_DEBUG) console.log('Loading auth state from storage:', { hasToken: !!token, hasUsername: !!username, userType });

            // Clear state if any required data is missing
            if (!token || !username || !userType) {
                if (AUTH_DEBUG) console.log('Missing required auth data in storage');
                await this.clearState(false);
                return;
            }

            // Set instance state
            this._token = token;
            this._userName = username;
            this._userType = userType;
            this._isLoggedIn = true;
            this._isInitialized = true;

            // Verificar token con el backend
            const isValid = await this.verifyToken();
            if (!isValid) {
                if (AUTH_DEBUG) console.log('Token verification failed during initialization');
                await this.clearState(true);
                return;
            }

            if (AUTH_DEBUG) console.log('Auth state loaded successfully:', { isLoggedIn: this._isLoggedIn, userName: this._userName, userType: this._userType });

            this.emit('change');
        } catch (error) {
            console.error('Error loading auth state:', error);
            await this.clearState(true);
        }
    }

    async verifyToken() {
        if (!this._token) return false;

        try {
            // Primero, verificar el estado de la sesión
            const debugResponse = await fetch('/api/auth/debug', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this._token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            const debugData = await debugResponse.json();
            if (AUTH_DEBUG) console.log('Session debug info:', debugData);

            if (!debugData.valid_token) {
                if (AUTH_DEBUG) console.log('Token not valid according to debug endpoint');
                await this.clearState(true);
                return false;
            }

            // Si el token es válido, obtener datos del usuario
            const response = await fetch('/api/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this._token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                if (AUTH_DEBUG) console.log('Token verification failed:', { status: response.status });
                await this.clearState(true);
                return false;
            }

            const data = await response.json();
            if (AUTH_DEBUG) console.log('Token verification successful:', data);

            // Actualizar datos del usuario si han cambiado
            if (data.username !== this._userName || data.user_type !== this._userType) {
                this._userName = data.username;
                this._userType = data.user_type;
                localStorage.setItem('username', data.username);
                localStorage.setItem('user_type', data.user_type);
                this.emit('change');
            }

            // Verificar y actualizar el token si se recibió uno nuevo
            const newToken = response.headers.get('Authorization')?.replace('Bearer ', '');
            if (newToken && newToken !== this._token) {
                if (AUTH_DEBUG) console.log('Updating token');
                this._token = newToken;
                localStorage.setItem('jwt_token', newToken);
                this.emit('change');
            }

            return true;
        } catch (error) {
            console.error('Error verifying token:', error);
            await this.clearState(true);
            return false;
        }
    }

    async clearState(emitChange = true) {
        if (AUTH_DEBUG) console.log('Clearing auth state');
        
        // Clear instance state
        this._token = null;
        this._userName = '';
        this._userType = '';
        this._isLoggedIn = false;
        
        // Clear storage
        try {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('username');
            localStorage.removeItem('user_type');
        } catch (error) {
            console.error('Error clearing localStorage:', error);
        }
        
        if (emitChange) {
            if (AUTH_DEBUG) console.log('Emitting auth state change after clear');
            this.emit('change');
        }
    }

    isLoggedIn() {
        const isValid = this._isLoggedIn && !!this._token;
        if (AUTH_DEBUG) console.log('Checking login state:', { _isLoggedIn: this._isLoggedIn, hasToken: !!this._token, isValid });
        return isValid;
    }

    isAdmin() {
        const isAdmin = this.isLoggedIn() && this._userType === 'admin';
        if (AUTH_DEBUG) console.log('Checking admin status:', { isLoggedIn: this._isLoggedIn, userType: this._userType, isAdmin });
        return isAdmin;
    }

    getUserName() {
        return this._userName;
    }

    getUserType() {
        return this._userType;
    }

    getToken() {
        return this._token;
    }

    login(token, username, userType) {
        console.log('Login attempt:', {
            hasToken: !!token,
            username,
            userType
        });

        if (!token || !username || !userType) {
            console.error('Login failed: Missing required data');
            return false;
        }

        try {
            // Clean the token if it has Bearer prefix
            const cleanToken = token.startsWith('Bearer ') ? token.replace('Bearer ', '') : token;
            
            // Clear any existing data first
            localStorage.clear();
            
            // Update storage with new data
            localStorage.setItem('jwt_token', cleanToken);
            localStorage.setItem('username', username);
            localStorage.setItem('user_type', userType);
            
            // Verify storage was updated
            const storedToken = localStorage.getItem('jwt_token');
            const storedUsername = localStorage.getItem('username');
            const storedUserType = localStorage.getItem('user_type');
            
            if (!storedToken || !storedUsername || !storedUserType) {
                throw new Error('Failed to store authentication data');
            }
            
            if (storedToken !== cleanToken || storedUsername !== username || storedUserType !== userType) {
                throw new Error('Stored authentication data mismatch');
            }
            
            // Update instance state
            this._token = cleanToken;
            this._userName = username;
            this._userType = userType;
            this._isLoggedIn = true;
            this._isInitialized = true;
            
            console.log('Login successful:', {
                isLoggedIn: this._isLoggedIn,
                userName: this._userName,
                userType: this._userType,
                hasToken: !!this._token,
                isInitialized: this._isInitialized
            });
            
            this.emit('change');
            return true;
        } catch (error) {
            console.error('Error during login:', error);
            this.clearState();
            return false;
        }
    }

    logout(redirect = true) {
        console.log('Logout initiated');
        this.clearState();
        
        if (redirect && !window.location.pathname.includes('login')) {
            window.location.href = '/login';
        }
    }

    validateAuth() {
        const hasToken = !!this._token;
        const hasUserData = !!this._userName && !!this._userType;
        const isValid = hasToken && hasUserData && this._isLoggedIn && this._isInitialized;

        if (AUTH_DEBUG) console.log('Validating auth state:', { hasToken, hasUserData, isLoggedIn: this._isLoggedIn, isInitialized: this._isInitialized, isValid });
        return isValid;
    }
}

const authStore = new AuthStore();

// Debug helper
window.debugAuthStore = () => {
    console.log('Auth Store Debug:', {
        isLoggedIn: authStore.isLoggedIn(),
        isAdmin: authStore.isAdmin(),
        userName: authStore.getUserName(),
        userType: authStore.getUserType(),
        hasToken: !!authStore.getToken(),
        localStorage: {
            token: !!localStorage.getItem('jwt_token'),
            username: localStorage.getItem('username'),
            userType: localStorage.getItem('user_type')
        }
    });
};

export default authStore;

