import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { signup, login, verifyOtp, logout as logoutAction } from '../store/slices/authSlice';
import { toast } from 'sonner';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const { user, isAuthenticated, isLoading, error, otpSent, emailOtpVerified, phoneOtpVerified } = useAppSelector(
    (state) => state.auth
  );

  const signupMutation = useMutation({
    mutationFn: async (credentials: {
      first_name: string;
      last_name: string;
      prefix: string;
      phone_number: string;
      email: string;
      password: string;
    }) => {
      const result = await dispatch(signup(credentials)).unwrap();
      return result;
    },
    onSuccess: (data) => {
      toast.success('Registration successful! Please verify your OTP.');
      // Navigate to OTP verification page
      navigate('/verify-otp');
    },
    onError: (error: string) => {
      toast.error(error || 'Registration failed');
    },
  });

  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const result = await dispatch(login(credentials)).unwrap();
      return result;
    },
    onSuccess: (data) => {
      toast.success('Login successful!');
      
      // Check if user needs OTP verification
      if (!data.data.user.is_verified) {
        navigate('/verify-otp');
      } else {
        navigate('/dashboard');
      }
    },
    onError: (error: string) => {
      toast.error(error || 'Login failed');
    },
  });

  const verifyOtpMutation = useMutation({
    mutationFn: async (otpData: {
      otp: string;
      otp_type: 'email' | 'phone';
      phone_number?: string;
      email?: string;
    }) => {
      const result = await dispatch(verifyOtp(otpData)).unwrap();
      return result;
    },
    onSuccess: (data) => {
      toast.success('OTP verified successfully!');
      
      // Check if both OTPs are verified
      if (data.data.user.is_verified) {
        navigate('/dashboard');
      }
    },
    onError: (error: string) => {
      toast.error(error || 'OTP verification failed');
    },
  });

  const logout = () => {
    dispatch(logoutAction());
    queryClient.clear(); // Clear all cached data
    navigate('/login');
    toast.success('Logged out successfully');
  };

  const clearError = () => {
    dispatch({ type: 'auth/clearError' });
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    otpSent,
    emailOtpVerified,
    phoneOtpVerified,
    signup: signupMutation.mutate,
    login: loginMutation.mutate,
    verifyOtp: verifyOtpMutation.mutate,
    logout,
    clearError,
    isSignupLoading: signupMutation.isPending,
    isLoginLoading: loginMutation.isPending,
    isOtpVerifying: verifyOtpMutation.isPending,
  };
};
