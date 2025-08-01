// routes.js
const routes = {
    home: {
        path: '/',
        view: 'nuevo-inventario',
        requiresAuth: true
    },
    admin: {
        path: '/admin',
        view: 'usuarios',
        requiresAuth: true,
        requiresAdmin: true
    },
    consultar: {
        path: '/consultar',
        view: 'consultar',
        requiresAuth: true
    },
    login: {
        path: '/login',
        view: 'login',
        requiresAuth: false
    }
};

export const getRouteByPath = (path) => {
    if (path === '/login') {
        return routes.login;
    }
    return Object.values(routes).find(route => route.path === path) || routes.home;
};

export const getRouteByView = (view) => {
    if (view === 'login') {
        return routes.login;
    }
    return Object.values(routes).find(route => route.view === view) || routes.home;
};

export const canAccessRoute = (route, isLoggedIn, isAdmin) => {
    if (route.path === '/login') return true;
    if (!route.requiresAuth) return true;
    if (!isLoggedIn) return false;
    if (route.requiresAdmin && !isAdmin) return false;
    return true;
};

export default routes; 