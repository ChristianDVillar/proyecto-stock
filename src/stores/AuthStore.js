import { EventEmitter } from 'events';

class AuthStore extends EventEmitter {
    constructor() {
        super();
        this.user = null; // Usuario logueado
        this.loggedIn = false; // Estado de autenticación
    }

    login(userName) {
        this.user = userName;
        this.loggedIn = true;
        this.emit('change'); // Emitir evento cuando el usuario se loguea
    }

    logout() {
        this.user = null;
        this.loggedIn = false;
        this.emit('change'); // Emitir evento cuando el usuario se desloguea
    }

    getUserName() {
        return this.user; // Devolver el nombre del usuario
    }

    isLoggedIn() {
        return this.loggedIn; // Devolver el estado de autenticación
    }
}

const authStore = new AuthStore();
export default authStore;
