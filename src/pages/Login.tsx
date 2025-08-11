import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { getDummyUserByEmail } from "@/data/users";

const Login = () => {
  const navigate = useNavigate();
  const { signIn } = useAuth();

  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("password123");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Try to find user in dummy data first
    const dummyUser = getDummyUserByEmail(email);
    
    if (dummyUser) {
      // Use dummy user data
      signIn(dummyUser);
      
      // Redirect based on role
      if (dummyUser.role === "delivery") {
        navigate("/delivery-partner");
      } else {
        navigate("/profile");
      }
    } else {
      // Create new user with 'user' role
      const user = {
        id: crypto.randomUUID(),
        name: "User",
        email,
        role: "user" as const,
      };
      signIn(user);
      navigate("/profile");
    }
  };

  return (
    <div className="min-h-screen bg-muted">
      <Navigation />
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-[55vh] flex items-center">
        <Card className="shadow-card w-full min-h-[380px] flex flex-col justify-center">
          <CardHeader>
            <CardTitle className="text-3xl text-center font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Login</CardTitle>
          </CardHeader>
          <CardContent className="w-full">
            <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-sm mx-auto">
              <Input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button type="submit" variant="hero" className="w-full">Sign In</Button>
            </form>
            <p className="text-sm text-muted-foreground mt-3 text-center">
              No account? <Link className="underline" to="/signup">Sign up</Link>
            </p>
            
            {/* Testing Info */}
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <p className="text-xs text-muted-foreground text-center">
                <strong>Testing:</strong><br />
                admin@example.com - Admin access<br />
                delivery@example.com - Delivery Partner access<br />
                user@example.com - Normal user access
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;


