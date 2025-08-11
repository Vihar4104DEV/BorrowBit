# Role-Based Access Control System

This application implements a role-based access control system with three user roles:

## User Roles

### 1. Guest (Not Logged In)
- **Access**: Home, Products
- **Navigation**: Only sees Home and Products in navbar
- **Features**: Can browse products and view product details

### 2. User (Normal User)
- **Access**: Home, Products, Bookings, Dashboard, Profile
- **Navigation**: Sees Home, Products, Bookings, Dashboard in navbar
- **Features**: Can manage their own bookings and view dashboard

### 3. Admin
- **Access**: Home, Products, Bookings, Customers, Dashboard, Profile
- **Navigation**: Sees all navigation items including Customers
- **Features**: Full access to all system features including customer management

## Testing the System

### Pre-configured Users
- **Admin**: `admin@example.com` / `password123`
- **Normal User**: `user@example.com` / `password123`
- **John Doe**: `john@example.com` / `password123`

### How to Test
1. **Login as Admin**:
   - Use `admin@example.com` to see all navigation items
   - Access Customers page (admin-only)
   - Access all other features

2. **Login as Normal User**:
   - Use `user@example.com` or create new account
   - See limited navigation (no Customers)
   - Access Bookings and Dashboard

3. **Guest Access**:
   - Don't login to see only Home and Products
   - Cannot access protected routes

### Role Switching (Testing)
- Go to Profile page after login
- Use "Set as Admin" or "Set as Normal User" buttons to test role changes
- Navigation will update immediately based on new role

## Implementation Details

### Files Modified
- `src/contexts/AuthContext.tsx` - Added role-based logic
- `src/components/Navigation.tsx` - Dynamic navigation based on role
- `src/components/RouteGuard.tsx` - Route protection component
- `src/App.tsx` - Protected routes with guards
- `src/pages/Login.tsx` - Role-based user creation
- `src/pages/Signup.tsx` - Default user role assignment
- `src/pages/Profile.tsx` - Role display and testing
- `src/data/users.ts` - Dummy user data

### Future API Integration
- Replace dummy data with API calls
- Store user roles in backend
- Implement proper authentication tokens
- Add role-based permissions for specific actions

## Security Notes
- Route protection prevents unauthorized access
- Navigation automatically updates based on user role
- All role checks happen on both client and route level
- Testing buttons should be removed in production
