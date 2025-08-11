# Authentication System Setup

This project has been updated with a complete authentication system using Redux Toolkit, React Query, and proper API integration.

## Features

- **User Registration**: Complete signup flow with form validation
- **User Login**: Secure login with API integration
- **OTP Verification**: Dual OTP verification (email + phone)
- **Redux State Management**: Centralized state management for authentication
- **React Query**: API caching and state synchronization
- **Protected Routes**: Route protection based on authentication status
- **Local Storage**: Secure token storage

## File Structure

```
src/
├── store/
│   ├── index.ts              # Redux store configuration
│   ├── hooks.ts              # Redux hooks (useAppDispatch, useAppSelector)
│   └── slices/
│       └── authSlice.ts      # Authentication state management
├── services/
│   └── api.ts                # API service layer
├── hooks/
│   └── useAuth.ts            # Authentication hooks with React Query
├── components/
│   └── ProtectedRoute.tsx    # Route protection component
└── pages/
    ├── Signup.tsx            # Updated signup page
    ├── Login.tsx             # Updated login page
    └── VerifyOtp.tsx         # New OTP verification page
```

## API Endpoints

### 1. User Registration
- **Path**: `POST /user/register/`
- **Request Body**:
  ```json
  {
    "first_name": "Vihar",
    "last_name": "Talaviya",
    "prefix": "Mr.",
    "phone_number": "9081522160",
    "email": "talaviyavihar41+9@gmail.com",
    "password": "Admin@123"
  }
  ```

### 2. User Login
- **Path**: `POST /user/login/`
- **Request Body**:
  ```json
  {
    "email": "talaviyavihar41@gmail.com",
    "password": "Admin@123"
  }
  ```

### 3. OTP Verification
- **Path**: `POST /user/verify-otp/`
- **Request Body**:
  ```json
  {
    "otp": "4567",
    "otp_type": "phone",
    "phone_number": "+919081522160"
  }
  ```

## Environment Configuration

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
```

## Authentication Flow

1. **Signup**: User fills registration form → API call → OTP sent to email/phone
2. **OTP Verification**: User enters OTPs → Verification → Account activated
3. **Login**: User enters credentials → API call → Access granted
4. **Token Storage**: Access and refresh tokens stored in localStorage
5. **Route Protection**: Protected routes check authentication status

## State Management

The authentication state includes:
- User information
- Access and refresh tokens
- Authentication status
- OTP verification status
- Loading states
- Error handling

## Usage Examples

### Using Authentication Hook
```tsx
import { useAuth } from '@/hooks/useAuth';

const MyComponent = () => {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  // Use authentication functions and state
};
```

### Protected Routes
```tsx
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

## Dependencies Added

- `@reduxjs/toolkit`: Redux state management
- `react-redux`: React bindings for Redux
- `@tanstack/react-query`: Data fetching and caching (already installed)

## Getting Started

1. Install dependencies: `npm install`
2. Create `.env` file with API URL
3. Start development server: `npm run dev`
4. Test the authentication flow

## Notes

- The system automatically handles token storage in localStorage
- OTP verification is required for new registrations
- Users are redirected based on their verification status
- All API calls include proper error handling
- React Query provides automatic caching and synchronization
