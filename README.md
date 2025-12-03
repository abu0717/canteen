ude # Canteen Management System

A comprehensive FastAPI-based canteen management system for managing cafes, menus, inventory, and orders with real-time WebSocket notifications.

## Features

- **User Authentication**: Register and login with JWT tokens
- **Role-Based Access**: Student, Cafe Owner, Cafe Worker, and Admin roles
- **Cafe Management**: Create and manage cafes
- **Menu Management**: Add, update, and delete menu items with categories
- **Inventory Tracking**: Track inventory items and quantities
- **Order Management**: Create and manage orders with status tracking
- **Real-time Notifications**: WebSocket support for instant order updates
- **Worker Management**: Assign cafe workers to cafes for order and inventory management
- **Public API**: View cafes and menus without authentication

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run database migrations:
```bash
alembic upgrade head
```

3. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

### Cafes (`/cafes`)
- `POST /cafes/` - Create a new cafe (cafe owner)
- `GET /cafes/` - Get all cafes owned by current user
- `GET /cafes/{cafe_id}` - Get cafe details
- `PUT /cafes/{cafe_id}` - Update cafe
- `GET /cafes/{cafe_id}/categories` - Get cafe categories
- `POST /cafes/categories` - Create a category
- `POST /cafes/menu` - Create a menu item
- `GET /cafes/{cafe_id}/menu` - Get cafe menu items
- `GET /cafes/menu/{menu_item_id}` - Get menu item details
- `PUT /cafes/menu/{menu_item_id}` - Update menu item
- `DELETE /cafes/menu/{menu_item_id}` - Delete menu item
- `POST /cafes/inventory` - Create inventory item
- `GET /cafes/{cafe_id}/inventory` - Get cafe inventory
- `PUT /cafes/inventory/{inventory_id}` - Update inventory item
- `DELETE /cafes/inventory/{inventory_id}` - Delete inventory item

### Orders (`/orders`)
- `POST /orders/` - Create a new order
- `GET /orders/` - Get user's orders
- `GET /orders/{order_id}` - Get order details
- `GET /orders/cafe/{cafe_id}` - Get all orders for a cafe (cafe owner)
- `PUT /orders/{order_id}` - Update order status (cafe owner)
- `DELETE /orders/{order_id}` - Cancel order

### Public (`/public`)
- `GET /public/cafes` - Get all cafes
- `GET /public/cafes/{cafe_id}` - Get cafe details
- `GET /public/cafes/{cafe_id}/menu` - Get cafe menu
- `GET /public/cafes/{cafe_id}/categories` - Get cafe categories

### Workers (`/workers`)
- `POST /workers/` - Assign a cafe worker to a cafe (cafe owner)
- `GET /workers/cafe/{cafe_id}` - Get all workers for a cafe (cafe owner)
- `GET /workers/my-cafes` - Get all cafes assigned to current worker
- `DELETE /workers/{worker_id}` - Remove worker from cafe (cafe owner)

### WebSocket Endpoints
- `WS /ws/cafe/{cafe_id}?token={jwt_token}` - Connect to cafe for real-time order notifications (cafe owners & workers)
- `WS /ws/orders?token={jwt_token}` - Connect to receive order status updates (students)

#### WebSocket Events

**For Cafe Owners/Workers** (`/ws/cafe/{cafe_id}`):
- `new_order` - Triggered when a student creates a new order
  ```json
  {
    "type": "new_order",
    "order_id": 123,
    "customer_name": "John Doe",
    "total_price": 25.50,
    "status": "pending",
    "items_count": 3,
    "note": "Extra spicy",
    "created_at": "2025-12-01T10:30:00"
  }
  ```

**For Students** (`/ws/orders`):
- `order_status_update` - Triggered when cafe updates order status
  ```json
  {
    "type": "order_status_update",
    "order_id": 123,
    "status": "preparing",
    "updated_by": "Cafe Staff"
  }
  ```

## Database Schema

### Users
- id (String, Primary Key)
- name (String)
- email (String, Unique)
- password_hash (String)
- role (String: student/cafe_owner/admin)

### Cafe Owner Profile
- id (String, Primary Key)
- user_id (String, Foreign Key -> User)
- total_orders (String)
- total_customers (String)
- total_revenue (String)

### Cafe
- id (String, Primary Key)
- name (String)
- location (String)
- owner_id (String, Foreign Key -> CafeOwnerProfile)

### Category
- id (String, Primary Key)
- cafe_id (String, Foreign Key -> Cafe)
- name (String)

### Menu Item
- id (String, Primary Key)
- cafe_id (String, Foreign Key -> Cafe)
- category_id (String, Foreign Key -> Category)
- image (String)
- name (String)
- description (String)
- price (Float)
- available (Boolean)

### Inventory
- id (String, Primary Key)
- cafe_id (String, Foreign Key -> Cafe)
- name (String)
- quantity (Float)
- kg (Float)
- description (String)
- cafe_owner_id (String, Foreign Key -> CafeOwnerProfile)

### Order
- id (Integer, Primary Key)
- account_id (String, Foreign Key -> User)
- cafe_id (String, Foreign Key -> Cafe)
- note (String)
- status (String: pending/preparing/completed/cancelled)
- total_price (Float)

### Order Item
- id (Integer, Primary Key)
- order_id (Integer, Foreign Key -> Order)
- menu_item_id (String, Foreign Key -> MenuItem)
- quantity (Integer)
- price (Float)

## User Roles

### Student
- Browse cafes and menus
- Create and manage their orders
- View order history
- Receive real-time order status updates via WebSocket

### Cafe Owner
- Manage their cafes
- Manage menu items and categories
- Track inventory
- Assign cafe workers to cafes
- View and update order status
- Receive real-time order notifications via WebSocket
- View cafe analytics

### Cafe Worker
- View assigned cafes
- Update order status for assigned cafes
- Manage inventory for assigned cafes
- Receive real-time order notifications via WebSocket

### Admin
- Full system access
- Manage all users and cafes

## Environment Variables

Create a `.env` file in the root directory:

```env
DB_URL=sqlite:///./test.db
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
```

Lint code:
```bash
flake8 app/
```

## License

MIT License

