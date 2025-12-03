# Canteen Management System - API Testing Guide

## Quick Start

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Open API documentation: http://localhost:8000/docs

## Testing Workflow

### Step 1: Register Users

#### Register a Student
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Student",
    "email": "student@example.com",
    "password": "password123",
    "role": "student"
  }'
```

#### Register a Cafe Owner
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Owner",
    "email": "owner@example.com",
    "password": "password123",
    "role": "cafe_owner"
  }'
```

#### Register a Cafe Worker
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Worker",
    "email": "worker@example.com",
    "password": "password123",
    "role": "cafe_worker"
  }'
```

### Step 2: Login and Get Tokens

#### Login as Cafe Owner
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response. Export it:
```bash
export OWNER_TOKEN="your_token_here"
```

#### Login as Student
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

```bash
export STUDENT_TOKEN="your_token_here"
```

#### Login as Worker
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "worker@example.com",
    "password": "password123"
  }'
```

```bash
export WORKER_TOKEN="your_token_here"
```

### Step 3: Create a Cafe (as Owner)

```bash
curl -X POST "http://localhost:8000/cafes/" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Delicious Canteen",
    "location": "Building A, Floor 1"
  }'
```

Save the cafe `id` from response:
```bash
export CAFE_ID="your_cafe_id_here"
```

### Step 4: Create Categories

```bash
curl -X POST "http://localhost:8000/cafes/categories" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cafe_id": "'$CAFE_ID'",
    "name": "Main Dishes"
  }'
```

Save category ID:
```bash
export CATEGORY_ID="your_category_id_here"
```

### Step 5: Add Menu Items

```bash
curl -X POST "http://localhost:8000/cafes/menu" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cafe_id": "'$CAFE_ID'",
    "category_id": "'$CATEGORY_ID'",
    "image": "https://example.com/burger.jpg",
    "name": "Classic Burger",
    "description": "Delicious beef burger with cheese",
    "price": 8.99,
    "available": true
  }'
```

Save menu item ID:
```bash
export MENU_ITEM_ID="your_menu_item_id_here"
```

### Step 6: Assign Worker to Cafe

First, get worker user_id:
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $WORKER_TOKEN"
```

Then assign:
```bash
curl -X POST "http://localhost:8000/workers/" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "worker_user_id_here",
    "cafe_id": "'$CAFE_ID'"
  }'
```

### Step 7: Create Inventory (as Owner or Worker)

```bash
curl -X POST "http://localhost:8000/cafes/inventory" \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cafe_id": "'$CAFE_ID'",
    "name": "Ground Beef",
    "quantity": 50,
    "kg": 25.5,
    "description": "Fresh ground beef for burgers",
    "cafe_owner_id": "owner_id_here"
  }'
```

### Step 8: Browse Public Cafes (No Auth Required)

```bash
curl -X GET "http://localhost:8000/public/cafes"
```

```bash
curl -X GET "http://localhost:8000/public/cafes/$CAFE_ID/menu"
```

### Step 9: Create an Order (as Student)

```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cafe_id": "'$CAFE_ID'",
    "note": "Extra cheese please",
    "items": [
      {
        "menu_item_id": "'$MENU_ITEM_ID'",
        "quantity": 2
      }
    ]
  }'
```

**Note:** When an order is created, cafe owners/workers connected via WebSocket will receive a real-time notification!

Save order ID:
```bash
export ORDER_ID="your_order_id_here"
```

### Step 10: Update Order Status (as Owner or Worker)

```bash
curl -X PUT "http://localhost:8000/orders/$ORDER_ID" \
  -H "Authorization: Bearer $WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "preparing"
  }'
```

**Note:** The student who created the order will receive a WebSocket notification!

### Step 11: Test WebSocket Connections

#### Option 1: Use the HTML Test Client

1. Open `websocket_test.html` in your browser
2. Select connection type (Cafe or Student)
3. Enter cafe ID (if cafe connection)
4. Paste your JWT token
5. Click Connect
6. Create orders or update statuses to see real-time notifications

#### Option 2: Use Python Test Client

```bash
python websocket_test_client.py
```

Follow the prompts and paste your token and cafe ID.

#### Option 3: Use JavaScript (Browser Console)

```javascript
const token = "YOUR_JWT_TOKEN";
const cafeId = "YOUR_CAFE_ID";
const ws = new WebSocket(`ws://localhost:8000/ws/cafe/${cafeId}?token=${token}`);

ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
ws.onerror = (error) => console.error('Error:', error);
```

## Testing Different Scenarios

### Scenario 1: Student Orders Flow
1. Student browses public cafes
2. Student creates an order
3. Cafe owner/worker receives WebSocket notification
4. Worker updates order status to "preparing"
5. Student receives status update via WebSocket
6. Worker marks order as "completed"
7. Student receives final status update

### Scenario 2: Worker Management
1. Owner assigns worker to cafe
2. Worker logs in and checks assigned cafes
3. Worker updates inventory
4. Worker processes orders
5. Owner can view all activities

### Scenario 3: Inventory Management
1. Owner creates inventory items
2. Worker updates quantities
3. Both can track stock levels
4. Update inventory when orders are processed

## Common Testing Tips

1. **Check Authentication**: Make sure tokens are valid and not expired
2. **WebSocket Connection**: Token must be passed as query parameter
3. **Order Creation**: Ensure menu items exist and are available
4. **Worker Assignment**: Workers must have `cafe_worker` role
5. **Real-time Testing**: Open multiple browser tabs/windows to test WebSocket notifications

## Error Handling

- **401 Unauthorized**: Token is missing or invalid
- **403 Forbidden**: User doesn't have permission
- **404 Not Found**: Resource doesn't exist
- **400 Bad Request**: Invalid data in request

## Performance Testing

Test with multiple concurrent users:

```bash
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/public/cafes
```

## WebSocket Load Testing

Use `websocket-bench` or similar tools:

```bash
npm install -g websocket-bench
websocket-bench -a 100 -c 10 ws://localhost:8000/ws/cafe/CAFE_ID?token=TOKEN
```

## Next Steps

- Add more menu items and categories
- Test order cancellation
- Test concurrent WebSocket connections
- Test with different user roles
- Monitor real-time notifications
- Test inventory updates
- Try bulk operations

