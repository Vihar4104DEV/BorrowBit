# User Authentication API Documentation

This document describes the user authentication APIs for the BorrowBit rental application.

## Base URL
```
/api/v1/user/
```

## Endpoints

### 1. User Registration
**POST** `/api/v1/user/register/`

Creates a new user account and sends OTP verification codes to both email and phone.

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "prefix": "Mr.",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Registration successful. OTP sent to email and phone.",
    "data": {}
}
```

**Validation Rules:**
- `first_name`, `last_name`, `email`, `phone_number`, `password` are required
- `prefix` is optional
- `password` must be at least 8 characters
- `email` must be unique
- `phone_number` must be unique and follow international format

### 2. User Login
**POST** `/api/v1/user/login/`

Authenticates users via email/password or mobile/OTP.

#### Email/Password Login
**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "password": "securepassword123",
    "login_type": "email"
}
```

#### Mobile/OTP Login
**Request Body:**
```json
{
    "phone_number": "+1234567890",
    "otp": "123456",
    "login_type": "mobile"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful via email.",
    "data": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "login_type": "email"
    }
}
```

**Notes:**
- Users must be verified (email and phone) before login
- JWT tokens are returned for authenticated requests
- Failed login attempts are tracked and accounts can be locked

### 3. Forgot Password
**POST** `/api/v1/user/forgot-password/`

Sends OTP to user's email for password reset.

**Request Body:**
```json
{
    "email": "john.doe@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "OTP sent to email for password reset.",
    "data": {}
}
```

### 4. OTP Verification
**POST** `/api/v1/user/verify-otp/`

Verifies OTP codes for email or phone verification.

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "otp": "123456",
    "otp_type": "email"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Email OTP verified successfully.",
    "data": {}
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "data": {}
}
```

**Common Error Messages:**
- `"Email already exists"` - Registration with duplicate email
- `"Phone number already exists"` - Registration with duplicate phone
- `"Invalid credentials"` - Wrong email/password combination
- `"User email/phone not verified"` - Login attempt before verification
- `"Invalid OTP"` - Wrong or expired OTP code
- `"OTP expired"` - OTP code has expired
- `"User with this email does not exist"` - Forgot password for non-existent user

## Security Features

- **Password Requirements**: Minimum 8 characters
- **Account Locking**: After 5 failed login attempts
- **OTP Expiration**: 10 minutes validity
- **JWT Authentication**: Secure token-based authentication
- **Audit Logging**: All user actions are logged
- **Rate Limiting**: Applied to sensitive endpoints

## OTP System

- **Generation**: 6-digit numeric codes
- **Expiration**: 10 minutes from creation
- **Delivery**: Email and SMS (SMS integration pending)
- **Verification**: One-time use, marked as verified after use

## Testing

Run the test suite:
```bash
python manage.py test user.tests
```

## Dependencies

- Django REST Framework
- Django Simple JWT
- Celery (for async notifications)
- Redis (for caching and sessions)

## Notes

- All timestamps are in UTC
- Phone numbers should follow international format (+1234567890)
- Email addresses are automatically normalized
- User verification is required before login
- Failed login attempts are tracked for security

