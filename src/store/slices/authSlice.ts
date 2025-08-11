import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, User, AuthData, OtpData } from '../../services/api';

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  otpSent: boolean;
  emailOtpVerified: boolean;
  phoneOtpVerified: boolean;
}

export interface SignupRequest {
  first_name: string;
  last_name: string;
  prefix: string;
  phone_number: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface OtpVerificationRequest {
  otp: string;
  otp_type: 'email' | 'phone';
  phone_number?: string;
  email?: string;
}

// Async thunks - Now using only the API service
export const signup = createAsyncThunk(
  'auth/signup',
  async (credentials: SignupRequest, { rejectWithValue }) => {
    try {
      const data = await apiService.signup(credentials);
      
      // Store tokens in localStorage
      localStorage.setItem('accessToken', data.data.access);
      localStorage.setItem('refreshToken', data.data.refresh);
      localStorage.setItem('userId', data.data.user.id);

      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Signup failed');
    }
  }
);

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginRequest, { rejectWithValue }) => {
    try {
      const data = await apiService.login(credentials);
      
      // Store tokens in localStorage
      localStorage.setItem('accessToken', data.data.access);
      localStorage.setItem('refreshToken', data.data.refresh);
      localStorage.setItem('userId', data.data.user.id);

      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Login failed');
    }
  }
);

export const verifyOtp = createAsyncThunk(
  'auth/verifyOtp',
  async (otpData: OtpVerificationRequest, { rejectWithValue }) => {
    try {
      const data = await apiService.verifyOtp(otpData);
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'OTP verification failed');
    }
  }
);

// Initial state
const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: !!localStorage.getItem('accessToken'),
  isLoading: false,
  error: null,
  otpSent: false,
  emailOtpVerified: false,
  phoneOtpVerified: false,
};

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.otpSent = false;
      state.emailOtpVerified = false;
      state.phoneOtpVerified = false;
      
      // Clear localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userId');
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    updateTokens: (state, action: PayloadAction<{ access: string; refresh: string }>) => {
      state.accessToken = action.payload.access;
      state.refreshToken = action.payload.refresh;
      
      // Update localStorage
      localStorage.setItem('accessToken', action.payload.access);
      localStorage.setItem('refreshToken', action.payload.refresh);
    },
  },
  extraReducers: (builder) => {
    // Signup
    builder
      .addCase(signup.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(signup.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data.user;
        state.accessToken = action.payload.data.access;
        state.refreshToken = action.payload.data.refresh;
        state.isAuthenticated = true;
        state.otpSent = true;
        state.error = null;
      })
      .addCase(signup.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Login
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data.user;
        state.accessToken = action.payload.data.access;
        state.refreshToken = action.payload.data.refresh;
        state.isAuthenticated = true;
        state.error = null;
        
        // Set OTP verification status based on user verification
        state.emailOtpVerified = !!action.payload.data.user.email_verified_at;
        state.phoneOtpVerified = !!action.payload.data.user.phone_verified_at;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // OTP Verification
    builder
      .addCase(verifyOtp.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(verifyOtp.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.data.user;
        state.error = null;
        
        // Update OTP verification status
        if (action.payload.data.user.email_verified_at) {
          state.emailOtpVerified = true;
        }
        if (action.payload.data.user.phone_verified_at) {
          state.phoneOtpVerified = true;
        }
      })
      .addCase(verifyOtp.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, logout, setUser, updateTokens } = authSlice.actions;
export default authSlice.reducer;
