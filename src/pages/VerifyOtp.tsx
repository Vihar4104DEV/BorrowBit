import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useAppSelector } from '../store/hooks';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Phone, Mail, CheckCircle, XCircle } from 'lucide-react';

const VerifyOtp: React.FC = () => {
  const { user, verifyOtp, isOtpVerifying, clearError } = useAuth();
  const { emailOtpVerified, phoneOtpVerified } = useAppSelector((state) => state.auth);
  
  const [emailOtp, setEmailOtp] = useState('');
  const [phoneOtp, setPhoneOtp] = useState('');
  const [activeTab, setActiveTab] = useState<'email' | 'phone'>('email');

  useEffect(() => {
    // Set active tab based on which OTP needs verification
    if (!emailOtpVerified && !phoneOtpVerified) {
      setActiveTab('email');
    } else if (!emailOtpVerified) {
      setActiveTab('email');
    } else if (!phoneOtpVerified) {
      setActiveTab('phone');
    }
  }, [emailOtpVerified, phoneOtpVerified]);

  const handleEmailOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailOtp.trim()) return;

    verifyOtp({
      otp: emailOtp,
      otp_type: 'email',
      email: user?.email,
    });
  };

  const handlePhoneOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneOtp.trim()) return;

    verifyOtp({
      otp: phoneOtp,
      otp_type: 'phone',
      phone_number: user?.phone_number,
    });
  };

  const handleOtpChange = (value: string, type: 'email' | 'phone') => {
    if (type === 'email') {
      setEmailOtp(value);
    } else {
      setPhoneOtp(value);
    }
  };

  // If both OTPs are verified, show success message
  if (emailOtpVerified && phoneOtpVerified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <CardTitle className="text-2xl">Verification Complete!</CardTitle>
            <CardDescription>
              Both email and phone OTPs have been verified successfully.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" onClick={() => window.location.href = '/dashboard'}>
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Verify Your Account</CardTitle>
          <CardDescription>
            Please verify your email and phone number to complete registration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'email' | 'phone')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email" disabled={emailOtpVerified}>
                <Mail className="w-4 h-4 mr-2" />
                Email {emailOtpVerified && <CheckCircle className="w-4 h-4 ml-1 text-green-500" />}
              </TabsTrigger>
              <TabsTrigger value="phone" disabled={phoneOtpVerified}>
                <Phone className="w-4 h-4 mr-2" />
                Phone {phoneOtpVerified && <CheckCircle className="w-4 h-4 ml-1 text-green-500" />}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="email" className="space-y-4">
              {emailOtpVerified ? (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    Email verified successfully!
                  </AlertDescription>
                </Alert>
              ) : (
                <form onSubmit={handleEmailOtpSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email-otp">Email OTP</Label>
                    <Input
                      id="email-otp"
                      type="text"
                      placeholder="Enter email OTP"
                      value={emailOtp}
                      onChange={(e) => handleOtpChange(e.target.value, 'email')}
                      maxLength={6}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={isOtpVerifying}>
                    {isOtpVerifying ? 'Verifying...' : 'Verify Email OTP'}
                  </Button>
                </form>
              )}
            </TabsContent>

            <TabsContent value="phone" className="space-y-4">
              {phoneOtpVerified ? (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    Phone verified successfully!
                  </AlertDescription>
                </Alert>
              ) : (
                <form onSubmit={handlePhoneOtpSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone-otp">Phone OTP</Label>
                    <Input
                      id="phone-otp"
                      type="text"
                      placeholder="Enter phone OTP"
                      value={phoneOtp}
                      onChange={(e) => handleOtpChange(e.target.value, 'phone')}
                      maxLength={6}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={isOtpVerifying}>
                    {isOtpVerifying ? 'Verifying...' : 'Verify Phone OTP'}
                  </Button>
                </form>
              )}
            </TabsContent>
          </Tabs>

          <div className="mt-6 text-center text-sm text-gray-600">
            <p>User ID: {user?.id}</p>
            <p>Email: {user?.email}</p>
            <p>Phone: {user?.phone_number}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VerifyOtp;
