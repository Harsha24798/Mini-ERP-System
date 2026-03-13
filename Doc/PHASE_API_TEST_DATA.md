# Phase API Test Data for Postman

This file contains ready-to-use API test data for completed backend phases.

Use this file to test APIs quickly in Postman without creating payloads manually.

---

## Postman Environment Setup

Create a Postman environment with these variables:

- `base_url` = `http://localhost:5000`
- `access_token` = (empty initially)
- `refresh_token` = (empty initially)
- `category_id` = (empty initially)
- `product_id` = (empty initially)
- `warehouse_id` = (empty initially)
- `to_warehouse_id` = (empty initially)

Recommended auth header format:

- `Authorization: Bearer {{access_token}}`

---

## Phase 2: Authentication API Test Data

Base path: `{{base_url}}/api/auth`

### 1. Register User

- Method: `POST`
- URL: `{{base_url}}/api/auth/register`
- Body (JSON):

```json
{
  "username": "postman_user_1",
  "email": "postman_user_1@test.com",
  "password": "password123",
  "first_name": "Postman",
  "last_name": "User",
  "phone": "+1-555-0101"
}
```

Expected: `201 Created`

### 2. Login User

- Method: `POST`
- URL: `{{base_url}}/api/auth/login`
- Body (JSON):

```json
{
  "username": "postman_user_1",
  "password": "password123"
}
```

Expected: `200 OK`

Save from response:

- `access_token` -> `{{access_token}}`
- `refresh_token` -> `{{refresh_token}}`

### 3. Refresh Access Token

- Method: `POST`
- URL: `{{base_url}}/api/auth/refresh`
- Headers:
  - `Authorization: Bearer {{refresh_token}}`

Expected: `200 OK` with new access token

### 4. Verify Token

- Method: `GET`
- URL: `{{base_url}}/api/auth/verify-token`
- Headers:
  - `Authorization: Bearer {{access_token}}`

Expected: `200 OK`, `valid: true`

### 5. Get Profile

- Method: `GET`
- URL: `{{base_url}}/api/auth/me`
- Headers:
  - `Authorization: Bearer {{access_token}}`

Expected: `200 OK` with user details

### 6. Update Profile

- Method: `PUT`
- URL: `{{base_url}}/api/auth/me`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "first_name": "PostmanUpdated",
  "last_name": "UserUpdated",
  "phone": "+1-555-9999"
}
```

Expected: `200 OK`

### 7. Change Password

- Method: `POST`
- URL: `{{base_url}}/api/auth/change-password`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "current_password": "password123",
  "new_password": "password456"
}
```

Expected: `200 OK`

Note:
- After changing password, login with new password.

### 8. Logout

- Method: `POST`
- URL: `{{base_url}}/api/auth/logout`
- Headers:
  - `Authorization: Bearer {{access_token}}`

Expected: `200 OK`

---

## Phase 3: Inventory API Test Data

Base path: `{{base_url}}/api/inventory`

Auth required for create/update/delete endpoints.

### A. Category APIs

#### 1. Create Category

- Method: `POST`
- URL: `{{base_url}}/api/inventory/categories`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "name": "Electronics",
  "description": "Electronic items"
}
```

Expected: `201 Created`

Save from response:

- `category.id` -> `{{category_id}}`

#### 2. List Categories

- Method: `GET`
- URL: `{{base_url}}/api/inventory/categories?search=elect&is_active=true`

Expected: `200 OK`

#### 3. Get Category By ID

- Method: `GET`
- URL: `{{base_url}}/api/inventory/categories/{{category_id}}`

Expected: `200 OK`

#### 4. Update Category

- Method: `PUT`
- URL: `{{base_url}}/api/inventory/categories/{{category_id}}`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "description": "Updated Electronics Category"
}
```

Expected: `200 OK`

#### 5. Delete Category (Soft Delete)

- Method: `DELETE`
- URL: `{{base_url}}/api/inventory/categories/{{category_id}}`
- Headers:
  - `Authorization: Bearer {{access_token}}`

Expected: `200 OK`

---

### B. Warehouse APIs

#### 1. Create Source Warehouse

- Method: `POST`
- URL: `{{base_url}}/api/inventory/warehouses`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "name": "Central Warehouse",
  "code": "CENTRAL",
  "city": "Delhi",
  "state": "Delhi",
  "country": "India",
  "phone": "9999999999"
}
```

Expected: `201 Created`

Save from response:

- `warehouse.id` -> `{{warehouse_id}}`

#### 2. Create Destination Warehouse (for transfer)

- Method: `POST`
- URL: `{{base_url}}/api/inventory/warehouses`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "name": "South Warehouse",
  "code": "SOUTH",
  "city": "Noida",
  "state": "UP",
  "country": "India",
  "phone": "8888888888"
}
```

Expected: `201 Created`

Save from response:

- `warehouse.id` -> `{{to_warehouse_id}}`

#### 3. List Warehouses

- Method: `GET`
- URL: `{{base_url}}/api/inventory/warehouses?search=warehouse&is_active=true`

Expected: `200 OK`

---

### C. Product APIs

#### 1. Create Product

- Method: `POST`
- URL: `{{base_url}}/api/inventory/products`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "sku": "COMP-001",
  "name": "Capacitor",
  "description": "Electronics component",
  "category_id": {{category_id}},
  "unit": "pcs",
  "price": "12.50",
  "cost": "10.00",
  "reorder_level": 10,
  "barcode": "8901234567890",
  "is_active": true
}
```

Expected: `201 Created`

Save from response:

- `product.id` -> `{{product_id}}`

#### 2. List Products

- Method: `GET`
- URL: `{{base_url}}/api/inventory/products?search=comp&category_id={{category_id}}&is_active=true`

Expected: `200 OK`

#### 3. Get Product By ID

- Method: `GET`
- URL: `{{base_url}}/api/inventory/products/{{product_id}}`

Expected: `200 OK`

#### 4. Update Product

- Method: `PUT`
- URL: `{{base_url}}/api/inventory/products/{{product_id}}`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "price": "17.50",
  "reorder_level": 3
}
```

Expected: `200 OK`

#### 5. Low Stock Products

- Method: `GET`
- URL: `{{base_url}}/api/inventory/products/low-stock`

Expected: `200 OK`

#### 6. Delete Product (Soft Delete)

- Method: `DELETE`
- URL: `{{base_url}}/api/inventory/products/{{product_id}}`
- Headers:
  - `Authorization: Bearer {{access_token}}`

Expected: `200 OK`

---

### D. Stock and Stock Movement APIs

#### 1. Stock IN

- Method: `POST`
- URL: `{{base_url}}/api/inventory/stocks/movement`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "product_id": {{product_id}},
  "warehouse_id": {{warehouse_id}},
  "movement_type": "IN",
  "quantity": 15,
  "notes": "Initial inward"
}
```

Expected: `201 Created`

#### 2. Stock OUT

- Method: `POST`
- URL: `{{base_url}}/api/inventory/stocks/movement`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "product_id": {{product_id}},
  "warehouse_id": {{warehouse_id}},
  "movement_type": "OUT",
  "quantity": 4,
  "notes": "Order dispatch"
}
```

Expected: `201 Created`

#### 3. Stock ADJUSTMENT

- Method: `POST`
- URL: `{{base_url}}/api/inventory/stocks/movement`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "product_id": {{product_id}},
  "warehouse_id": {{warehouse_id}},
  "movement_type": "ADJUSTMENT",
  "quantity": 2,
  "notes": "Manual stock count correction"
}
```

Expected: `201 Created`

#### 4. Stock TRANSFER

- Method: `POST`
- URL: `{{base_url}}/api/inventory/stocks/movement`
- Headers:
  - `Authorization: Bearer {{access_token}}`
- Body (JSON):

```json
{
  "product_id": {{product_id}},
  "warehouse_id": {{warehouse_id}},
  "to_warehouse_id": {{to_warehouse_id}},
  "movement_type": "TRANSFER",
  "quantity": 3,
  "notes": "Rebalancing stock"
}
```

Expected: `201 Created`

#### 5. List Stocks

- Method: `GET`
- URL: `{{base_url}}/api/inventory/stocks?product_id={{product_id}}&warehouse_id={{warehouse_id}}`

Expected: `200 OK`

#### 6. List Stock Movements

- Method: `GET`
- URL: `{{base_url}}/api/inventory/stocks/movements?product_id={{product_id}}&movement_type=in`

Expected: `200 OK`

---

## Upcoming Phases (Template)

Add each upcoming API phase here after completion using the same format.

### Phase X: <Module Name>

- Base path:
- Auth requirements:
- Endpoint list:
- Postman test payloads:
- Expected responses:
- Variables to save from responses:

Copy/paste template:

```md
## Phase X: <Module Name>

Base path: `{{base_url}}/<module-path>`

### 1. <Endpoint Name>
- Method:
- URL:
- Headers:
- Body:
- Expected:
- Save variable:
```

---

## Suggested Testing Sequence

1. Register user
2. Login user and save tokens
3. Create category
4. Create two warehouses
5. Create product
6. Create stock IN movement
7. Create stock OUT movement
8. Create stock TRANSFER movement
9. Verify stocks and movements list

This sequence avoids dependency errors and keeps IDs available for all requests.
