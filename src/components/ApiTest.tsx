import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { apiService } from '../services/api';

const ApiTest: React.FC = () => {
  const [testData, setTestData] = useState({
    email: 'test@example.com',
    password: 'testpassword',
    first_name: 'Test',
    last_name: 'User',
    prefix: 'Mr.',
    phone_number: '1234567890',
  });
  
  const [results, setResults] = useState<any>({});
  const [loading, setLoading] = useState<string | null>(null);

  const testLogin = async () => {
    setLoading('login');
    try {
      const result = await apiService.login({
        email: testData.email,
        password: testData.password,
      });
      setResults(prev => ({ ...prev, login: { success: true, data: result } }));
    } catch (error) {
      setResults(prev => ({ 
        ...prev, 
        login: { 
          success: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        } 
      }));
    } finally {
      setLoading(null);
    }
  };

  const testSignup = async () => {
    setLoading('signup');
    try {
      const result = await apiService.signup({
        first_name: testData.first_name,
        last_name: testData.last_name,
        prefix: testData.prefix,
        phone_number: testData.phone_number,
        email: testData.email,
        password: testData.password,
      });
      setResults(prev => ({ ...prev, signup: { success: true, data: result } }));
    } catch (error) {
      setResults(prev => ({ 
        ...prev, 
        signup: { 
          success: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        } 
      }));
    } finally {
      setLoading(null);
    }
  };

  const testOtp = async () => {
    setLoading('otp');
    try {
      const result = await apiService.verifyOtp({
        otp: '1234',
        otp_type: 'email',
        email: testData.email,
      });
      setResults(prev => ({ ...prev, otp: { success: true, data: result } }));
    } catch (error) {
      setResults(prev => ({ 
        ...prev, 
        otp: { 
          success: false, 
          error: error instanceof Error ? error.message : 'Unknown error' 
        } 
      }));
    } finally {
      setLoading(null);
    }
  };

  const clearResults = () => {
    setResults({});
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>API Connection Test</CardTitle>
        <p className="text-sm text-muted-foreground">
          Test your API endpoints to debug CORS and connection issues
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Test Data Inputs */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              value={testData.email}
              onChange={(e) => setTestData(prev => ({ ...prev, email: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={testData.password}
              onChange={(e) => setTestData(prev => ({ ...prev, password: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="first_name">First Name</Label>
            <Input
              id="first_name"
              value={testData.first_name}
              onChange={(e) => setTestData(prev => ({ ...prev, first_name: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone_number">Phone Number</Label>
            <Input
              id="phone_number"
              value={testData.phone_number}
              onChange={(e) => setTestData(prev => ({ ...prev, phone_number: e.target.value }))}
            />
          </div>
        </div>

        {/* Test Buttons */}
        <div className="flex gap-4">
          <Button 
            onClick={testLogin} 
            disabled={loading === 'login'}
            variant="outline"
          >
            {loading === 'login' ? 'Testing...' : 'Test Login'}
          </Button>
          <Button 
            onClick={testSignup} 
            disabled={loading === 'signup'}
            variant="outline"
          >
            {loading === 'signup' ? 'Testing...' : 'Test Signup'}
          </Button>
          <Button 
            onClick={testOtp} 
            disabled={loading === 'otp'}
            variant="outline"
          >
            {loading === 'otp' ? 'Testing...' : 'Test OTP'}
          </Button>
          <Button onClick={clearResults} variant="destructive">
            Clear Results
          </Button>
        </div>

        {/* Results Display */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Test Results:</h3>
          
          {Object.entries(results).map(([testName, result]: [string, any]) => (
            <div key={testName} className="border rounded-lg p-4">
              <h4 className="font-medium capitalize mb-2">{testName} Test</h4>
              {result.success ? (
                <div className="text-green-600">
                  <p>✅ Success!</p>
                  <pre className="mt-2 text-xs bg-green-50 p-2 rounded overflow-auto">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="text-red-600">
                  <p>❌ Failed: {result.error}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Environment Info */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-semibold mb-2">Environment Info:</h3>
          <div className="text-sm space-y-1">
            <p><strong>API URL:</strong> {import.meta.env.VITE_API_URL || 'Not set'}</p>
            <p><strong>Node Env:</strong> {import.meta.env.MODE}</p>
            <p><strong>Base URL:</strong> {window.location.origin}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ApiTest;
