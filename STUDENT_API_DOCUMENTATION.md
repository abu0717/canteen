# Student API Documentation

This document provides comprehensive documentation for all API endpoints available to students in the Canteen Management System.

## Base URL
```
http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Login
**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "name": "John Doe",
    "role": "student"
  }
}
```

---

## 📍 Public Endpoints (No Authentication Required)

### 1. Get All Cafes
**Endpoint:** `GET /public/cafes`

**Description:** Retrieve a list of all available cafes.

**Response:**
```json
[
  {
    "id": "1",
    "name": "Main Campus Cafe",
    "location": "Building A, Ground Floor",
    "image": "/uploads/cafes/main-cafe.jpg",
    "owner_id": "owner-uuid",
    "rating": 4.5,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-03T15:30:00"
  }
]
```

### 2. Get Cafe Details
**Endpoint:** `GET /public/cafes/{cafe_id}`

**Description:** Get detailed information about a specific cafe.

**Path Parameters:**
- `cafe_id` (string): The unique identifier of the cafe

**Response:**
```json
{
  "id": "1",
  "name": "Main Campus Cafe",
  "location": "Building A, Ground Floor",
  "image": "/uploads/cafes/main-cafe.jpg",
  "owner_id": "owner-uuid",
  "rating": 4.5,
  "created_at": "2025-12-01T10:00:00",
  "updated_at": "2025-12-03T15:30:00"
}
```

### 3. Get Cafe Menu
**Endpoint:** `GET /public/cafes/{cafe_id}/menu`

**Description:** Retrieve all available menu items for a specific cafe.

**Path Parameters:**
- `cafe_id` (string): The unique identifier of the cafe

**Response:**
```json
[
  {
    "id": "menu-item-1",
    "cafe_id": "1",
    "category_id": "cat-1",
    "image": "/uploads/menu/burger.jpg",
    "name": "Cheeseburger",
    "description": "Delicious beef burger with cheese",
    "price": 8.99,
    "available": true,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-03T15:30:00"
  },
  {
    "id": "menu-item-2",
    "cafe_id": "1",
    "category_id": "cat-2",
    "image": "/uploads/menu/coffee.jpg",
    "name": "Cappuccino",
    "description": "Rich espresso with steamed milk",
    "price": 4.50,
    "available": true,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-03T15:30:00"
  }
]
```

### 4. Get Cafe Categories
**Endpoint:** `GET /public/cafes/{cafe_id}/categories`

**Description:** Get all categories for a specific cafe's menu.

**Path Parameters:**
- `cafe_id` (string): The unique identifier of the cafe

**Response:**
```json
[
  {
    "id": "cat-1",
    "cafe_id": "1",
    "name": "Main Dishes"
  },
  {
    "id": "cat-2",
    "cafe_id": "1",
    "name": "Beverages"
  }
]
```

### 5. Get Menu Items by Category
**Endpoint:** `GET /public/categories/{category_id}/menu`

**Description:** Get all menu items within a specific category.

**Path Parameters:**
- `category_id` (string): The unique identifier of the category

**Response:**
```json
[
  {
    "id": "menu-item-1",
    "cafe_id": "1",
    "category_id": "cat-1",
    "image": "/uploads/menu/burger.jpg",
    "name": "Cheeseburger",
    "description": "Delicious beef burger with cheese",
    "price": 8.99,
    "available": true,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-03T15:30:00"
  }
]
```

### 6. Get Cafes by Public Category
**Endpoint:** `GET /public/categories/{category_name}/cafes`

**Description:** Find cafes that belong to a specific public category (e.g., "Fast Food", "Coffee Shop").

**Path Parameters:**
- `category_name` (string): The name of the public category

**Response:**
```json
[
  {
    "id": "1",
    "name": "Main Campus Cafe",
    "location": "Building A, Ground Floor",
    "image": "/uploads/cafes/main-cafe.jpg",
    "owner_id": "owner-uuid",
    "rating": 4.5,
    "created_at": "2025-12-01T10:00:00",
    "updated_at": "2025-12-03T15:30:00"
  }
]
```

---

## 🛒 Order Management (Authentication Required)

### 1. Create Order
**Endpoint:** `POST /orders/`

**Description:** Create a new order with multiple items.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "cafe_id": "1",
  "note": "No onions please",
  "items": [
    {
      "menu_item_id": "menu-item-1",
      "quantity": 2,
      "scheduled": false,
      "scheduled_time": null
    },
    {
      "menu_item_id": "menu-item-2",
      "quantity": 1,
      "scheduled": false,
      "scheduled_time": null
    }
  ]
}
```

**Response:**
```json
{
  "id": 42,
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "account_name": "John Doe",
  "cafe_id": "1",
  "cafe_name": "Main Campus Cafe",
  "note": "No onions please",
  "status": "pending",
  "total_price": 22.48,
  "items": [
    {
      "id": 1,
      "order_id": 42,
      "menu_item_id": "menu-item-1",
      "menu_item_name": "Cheeseburger",
      "quantity": 2,
      "price": 8.99,
      "scheduled": false,
      "scheduled_time": null,
      "created_at": "2025-12-03T12:00:00",
      "updated_at": "2025-12-03T12:00:00"
    },
    {
      "id": 2,
      "order_id": 42,
      "menu_item_id": "menu-item-2",
      "menu_item_name": "Cappuccino",
      "quantity": 1,
      "price": 4.50,
      "scheduled": false,
      "scheduled_time": null,
      "created_at": "2025-12-03T12:00:00",
      "updated_at": "2025-12-03T12:00:00"
    }
  ],
  "created_at": "2025-12-03T12:00:00",
  "updated_at": "2025-12-03T12:00:00"
}
```

### 2. Get Order History
**Endpoint:** `GET /orders/history`

**Description:** Retrieve all orders placed by the authenticated student.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
[
  {
    "id": 42,
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "account_name": "John Doe",
    "cafe_id": "1",
    "cafe_name": "Main Campus Cafe",
    "note": "No onions please",
    "status": "completed",
    "total_price": 22.48,
    "items": [
      {
        "id": 1,
        "order_id": 42,
        "menu_item_id": "menu-item-1",
        "menu_item_name": "Cheeseburger",
        "quantity": 2,
        "price": 8.99,
        "scheduled": false,
        "scheduled_time": null,
        "created_at": "2025-12-03T12:00:00",
        "updated_at": "2025-12-03T12:00:00"
      }
    ],
    "created_at": "2025-12-03T12:00:00",
    "updated_at": "2025-12-03T12:30:00"
  }
]
```

### 3. Get Order Details
**Endpoint:** `GET /orders/{order_id}`

**Description:** Get detailed information about a specific order.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Path Parameters:**
- `order_id` (integer): The unique identifier of the order

**Response:**
```json
{
  "id": 42,
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "account_name": "John Doe",
  "cafe_id": "1",
  "cafe_name": "Main Campus Cafe",
  "note": "No onions please",
  "status": "completed",
  "total_price": 22.48,
  "items": [
    {
      "id": 1,
      "order_id": 42,
      "menu_item_id": "menu-item-1",
      "menu_item_name": "Cheeseburger",
      "quantity": 2,
      "price": 8.99,
      "scheduled": false,
      "scheduled_time": null,
      "created_at": "2025-12-03T12:00:00",
      "updated_at": "2025-12-03T12:00:00"
    }
  ],
  "created_at": "2025-12-03T12:00:00",
  "updated_at": "2025-12-03T12:30:00"
}
```

### 4. Cancel Order
**Endpoint:** `DELETE /orders/{order_id}`

**Description:** Cancel an order (only allowed if status is "pending").

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Path Parameters:**
- `order_id` (integer): The unique identifier of the order

**Response:**
```
HTTP 204 No Content
```

**Error Response (if order cannot be cancelled):**
```json
{
  "detail": "Cannot cancel order with status: preparing"
}
```

---

## ⭐ Feedback Management (Authentication Required)

### 1. Submit Feedback
**Endpoint:** `POST /feedback/`

**Description:** Submit feedback for a completed order. Each order can only have one feedback.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "order_id": 42,
  "rating": 4.5,
  "comment": "Great food and fast service!"
}
```

**Response:**
```json
{
  "id": "feedback-uuid",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_name": "John Doe",
  "order_id": 42,
  "comment": "Great food and fast service!",
  "rating": 4.5,
  "cafe_id": "1",
  "created_at": "2025-12-03T13:00:00"
}
```

**Validation Rules:**
- Order must exist and be completed
- Student must own the order
- Only one feedback per order allowed
- Rating must be between 0 and 5

**Error Responses:**
```json
{
  "detail": "Order not found"
}
```
```json
{
  "detail": "You can only provide feedback for your own orders"
}
```
```json
{
  "detail": "Feedback already exists for this order"
}
```

### 2. Get Cafe Feedbacks
**Endpoint:** `GET /feedback/cafe/{cafe_id}`

**Description:** View all feedbacks for a specific cafe (public access).

**Path Parameters:**
- `cafe_id` (string): The unique identifier of the cafe

**Response:**
```json
[
  {
    "id": "feedback-uuid-1",
    "student_id": "550e8400-e29b-41d4-a716-446655440000",
    "student_name": "John Doe",
    "order_id": 42,
    "comment": "Great food and fast service!",
    "rating": 4.5,
    "cafe_id": "1",
    "created_at": "2025-12-03T13:00:00"
  },
  {
    "id": "feedback-uuid-2",
    "student_id": "another-student-uuid",
    "student_name": "Jane Smith",
    "order_id": 38,
    "comment": "Delicious coffee, highly recommend!",
    "rating": 5.0,
    "cafe_id": "1",
    "created_at": "2025-12-02T10:30:00"
  }
]
```

### 3. Get My Feedbacks
**Endpoint:** `GET /feedback/my-feedbacks`

**Description:** Retrieve all feedbacks submitted by the authenticated student.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
[
  {
    "id": "feedback-uuid",
    "student_id": "550e8400-e29b-41d4-a716-446655440000",
    "student_name": "John Doe",
    "order_id": 42,
    "comment": "Great food and fast service!",
    "rating": 4.5,
    "cafe_id": "1",
    "created_at": "2025-12-03T13:00:00"
  }
]
```

### 4. Check Order Feedback
**Endpoint:** `GET /feedback/order/{order_id}`

**Description:** Check if feedback exists for a specific order.

**Path Parameters:**
- `order_id` (integer): The unique identifier of the order

**Response (if feedback exists):**
```json
{
  "id": "feedback-uuid",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_name": "John Doe",
  "order_id": 42,
  "comment": "Great food and fast service!",
  "rating": 4.5,
  "cafe_id": "1",
  "created_at": "2025-12-03T13:00:00"
}
```

**Response (if no feedback):**
```json
{
  "detail": "Feedback not found for this order"
}
```

### 5. Delete Feedback
**Endpoint:** `DELETE /feedback/{feedback_id}`

**Description:** Delete your own feedback.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Path Parameters:**
- `feedback_id` (string): The unique identifier of the feedback

**Response:**
```
HTTP 204 No Content
```

**Error Response (if not owner):**
```json
{
  "detail": "You can only delete your own feedback"
}
```

---

## 📊 Order Status Flow

Orders go through the following status transitions:

1. **pending** - Order created, waiting for cafe acceptance
2. **preparing** - Cafe is preparing the order
3. **ready** - Order is ready for pickup
4. **completed** - Order has been picked up/delivered
5. **cancelled** - Order was cancelled

**Note:** Students can only cancel orders with "pending" status.

---

## 🔍 Common Use Cases

### Complete Order Flow
1. Browse cafes: `GET /public/cafes`
2. View cafe menu: `GET /public/cafes/{cafe_id}/menu`
3. Create order: `POST /orders/`
4. Check order status: `GET /orders/{order_id}`
5. After completion, submit feedback: `POST /feedback/`

### Browsing by Category
1. Get public categories: `GET /public/categories/{category_name}/cafes`
2. View cafe menu: `GET /public/cafes/{cafe_id}/menu`
3. Filter by category: `GET /public/categories/{category_id}/menu`

### Order Management
1. View all orders: `GET /orders/history`
2. Check specific order: `GET /orders/{order_id}`
3. Cancel if needed: `DELETE /orders/{order_id}`

---

## 💡 Tips

- **Image URLs:** All image paths are relative (e.g., `/uploads/cafes/image.jpg`). Prepend your base URL to display images.
- **Timestamps:** All timestamps are in ISO 8601 format.
- **Currency:** All prices are in USD (or your local currency).
- **Authentication:** Keep your JWT token secure and refresh it when expired.
- **Order Cancellation:** Only "pending" orders can be cancelled by students.
- **Feedback:** You can only submit feedback for completed orders that you own.

---

## ❌ Common Error Codes

- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - You don't have permission to perform this action
- `404 Not Found` - Resource doesn't exist
- `400 Bad Request` - Invalid request data
- `422 Unprocessable Entity` - Validation error in request body

---

## 📞 Support

For issues or questions, please contact the system administrator.
