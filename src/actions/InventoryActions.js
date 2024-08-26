import AppDispatcher from '../dispatcher/AppDispatcher';

export const InventoryActions = {
    addItem(item) {
        AppDispatcher.dispatch({
            actionType: 'ADD_ITEM',
            item: item,
        });
    },
    deleteItem(itemId) {
        AppDispatcher.dispatch({
            actionType: 'DELETE_ITEM',
            itemId: itemId,
        });
    },
    updateItem(item) {
        AppDispatcher.dispatch({
            actionType: 'UPDATE_ITEM',
            item: item,
        });
    }
};
