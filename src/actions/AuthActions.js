import AppDispatcher from '../dispatcher/AppDispatcher';

export const AuthActions = {
    loginUser(username) {
        AppDispatcher.dispatch({
            actionType: 'LOGIN_USER',
            username: username,
        });
    },
    logoutUser() {
        AppDispatcher.dispatch({
            actionType: 'LOGOUT_USER',
        });
    }
};
