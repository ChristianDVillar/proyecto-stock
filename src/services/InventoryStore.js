import { EventEmitter } from 'events';
import AppDispatcher from '../dispatcher/AppDispatcher';

let _inventory = [];

class InventoryStore extends EventEmitter {
    getAllItems() {
        return _inventory;
    }

    handleActions(action) {
        switch (action.actionType) {
            case 'ADD_ITEM':
                _inventory.push(action.item);
                this.emit('change');
                break;
            case 'DELETE_ITEM':
                _inventory = _inventory.filter(item => item.id !== action.itemId);
                this.emit('change');
                break;
            case 'UPDATE_ITEM':
                _inventory = _inventory.map(item =>
                    item.id === action.item.id ? action.item : item
                );
                this.emit('change');
                break;
            default:
                break;
        }
    }
}

const inventoryStore = new InventoryStore();
AppDispatcher.register(inventoryStore.handleActions.bind(inventoryStore));
export default inventoryStore;
