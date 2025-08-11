import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";

const Signup = () => {
  const navigate = useNavigate();
  const { signIn } = useAuth();

  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !name || !phone || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    // Create user with 'user' role by default
    const newUser = {
      id: crypto.randomUUID(),
      name,
      email,
      phone,
      role: "user" as const,
    };

    signIn(newUser);
    navigate("/profile");
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-2xl">Create your account</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input placeholder="Your Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input placeholder="Your Name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input placeholder="Your Phone" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
              <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              <Input placeholder="Confirm Password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />

              {error && <div className="text-sm text-destructive">{error}</div>}

              <Button type="submit" variant="hero" className="w-full">Sign Up</Button>
            </form>
            <p className="text-sm text-muted-foreground mt-3">
              Already have an account? <Link className="underline" to="/login">Login</Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Signup;


