# TableOne — Restaurant Booking API

A FastAPI-based restaurant booking platform with JWT authentication, role-based access control, and full CRUD for restaurants, dishes, tables, and bookings.

---

## Project Structure

```
RESTAURANT_BOOKING/
├── router/
│   ├── __init__.py
│   ├── auth.py          # Register & login endpoints
│   ├── booking.py       # Booking creation & cancellation
│   ├── dishes.py        # Dish management
│   ├── restaurants.py   # Restaurant management
│   └── tables.py        # Table management
├── .env                 # Environment variables (never commit this)
├── database.py          # SQLAlchemy engine & session factory
├── main.py              # FastAPI app entry point
├── model.py             # ORM models
├── schema.py            # Pydantic request/response schemas
├── services.py          # JWT, hashing, and auth dependencies
├── requirements.txt
└── restaurant_booking.html   # Frontend (single-file)
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd RESTAURANT_BOOKING
python -m venv myenv
source myenv/bin/activate        # Windows: myenv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DB_URL=postgresql://user:password@localhost:5432/restaurant_booking
SECRET_KEY=your-long-random-secret-key-here
```

> **Never commit `.env` to version control.** Generate a strong `SECRET_KEY` with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Authentication

The API uses **JWT Bearer tokens**. All routes except registration and login require a valid token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "securepassword",
  "role": "customer"
}
```

Roles: `customer` · `admin` · `owner`

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "jane@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

---

## Roles & Permissions

| Action | Customer | Admin | Owner |
|--------|----------|-------|-------|
| View restaurants | ✅ | ✅ | ✅ |
| Add / delete restaurant | ❌ | ❌ | ✅ |
| View dishes | ✅ | ✅ | ✅ |
| Add / delete dish | ❌ | ❌ | ✅ |
| View tables | ❌ | ✅ | ✅ |
| Add / delete table | ❌ | ✅ | ✅ |
| Create booking | ✅ | ✅ | ✅ |
| Cancel own booking | ✅ | ✅ | ✅ |

---

## API Endpoints

### Restaurants — `/restaurants`

| Method | Path | Description | Role |
|--------|------|-------------|------|
| GET | `/restaurants` | List all restaurants | Any |
| GET | `/restaurants/by-id/{id}` | Get restaurant by ID | Any |
| GET | `/restaurants/by-name/{name}` | Get restaurant by name | Any |
| POST | `/restaurants` | Create a restaurant | Owner |
| PUT | `/restaurants/{id}` | Update a restaurant | Owner |
| DELETE | `/restaurants/{id}` | Delete a restaurant | Owner |

**Create restaurant body:**
```json
{
  "name": "The Golden Fork",
  "location": "Mumbai, Bandra",
  "admin_id": 1,
  "table_count": 8
}
```

---

### Dishes — `/dishes`

| Method | Path | Description | Role |
|--------|------|-------------|------|
| GET | `/dishes` | List all dishes | Any |
| GET | `/dishes/by-id/{id}` | Get dish by ID | Any |
| GET | `/dishes/by-name/{name}` | Get dish by name | Any |
| POST | `/dishes` | Add a dish | Owner |
| PUT | `/dishes/{id}` | Update a dish | Owner |
| DELETE | `/dishes/{id}` | Delete a dish | Owner |

**Create dish body:**
```json
{
  "name": "Grilled Sea Bass",
  "price": 850.00,
  "description": "Served with lemon butter sauce"
}
```

---

### Tables — `/tables`

| Method | Path | Description | Role |
|--------|------|-------------|------|
| GET | `/tables` | List all tables | Owner / Admin |
| GET | `/tables/{table_id}` | Get table by ID | Owner / Admin |
| POST | `/tables` | Add a table | Owner / Admin |
| DELETE | `/tables/{table_id}` | Delete a table | Owner / Admin |

**Create table body:**
```json
{
  "restaurant_id": 1,
  "number": 5,
  "capacity": 4,
  "booking_status": false
}
```

---

### Bookings — `/booking`

| Method | Path | Description | Role |
|--------|------|-------------|------|
| POST | `/booking/` | Create a booking | Any authenticated |
| DELETE | `/booking/{booking_id}` | Cancel a booking | Booking owner only |

**Create booking body:**
```json
{
  "restaurant_id": 1,
  "date": "2025-08-15T19:30:00",
  "guests": 3
}
```

The API automatically selects an available table with sufficient capacity for the requested date. `user_id` and `table_id` are resolved server-side — do not pass them in the request.

**Booking logic:**
1. Verify the restaurant exists.
2. Find tables in the restaurant where `capacity >= guests` and `booking_status = false`.
3. From those, check for no existing active booking on the same date.
4. Assign the first conflict-free table.
5. Mark the table as booked and create the booking record.

**Cancel booking:** Only the user who created the booking can cancel it. Cancellation sets `booking.status = false` (soft delete, preserves history) and frees the table if no other active bookings exist for it.

---

## Data Models

```
User         — id, name, email, password (hashed), role
Restaurant   — id, name, location, admin_id → User, table_count
Table        — id, restaurant_id → Restaurant, number, capacity, booking_status
Booking      — id, user_id → User, restaurant_id → Restaurant, table_id → Table, date, guests, status
Dish         — id, name, price, description
```

---

## Frontend

Open `restaurant_booking.html` in a browser while the API server is running. No build step required.

The frontend connects to `http://localhost:8000` by default. To change the API URL, edit the first line of the `<script>` block:

```js
const API = 'http://localhost:8000';
```

**Features:** login/register, restaurant browser, menu viewer, table management (owner/admin), and booking creation with automatic table selection.

---

## Requirements

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary       # or aiosqlite for SQLite
python-jose[cryptography]
bcrypt
python-dotenv
pydantic
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## Notes

- Tokens expire after **30 minutes**. Re-login to get a new token.
- Passwords are hashed with **bcrypt** before storage — plain-text passwords are never saved.
- The `booking_status` flag on `Table` is a quick availability indicator. Date-level conflict checking is also performed on booking creation for accuracy.
- `SECRET_KEY` must be set in `.env` — the server will refuse to start without it.