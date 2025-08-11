import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Products from "./pages/Products";
import Dashboard from "./pages/Dashboard";
import Bookings from "./pages/Bookings";
import Customers from "./pages/Customers";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Profile from "./pages/Profile";
import { AuthProvider } from "@/contexts/AuthContext";
import { ChatbotButton } from "@/components/ChatbotButton";
import Chat from "@/pages/Chat";
import ProductDetail from "@/pages/ProductDetail";
import { RouteGuard } from "@/components/RouteGuard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:id" element={<ProductDetail />} />
            
            {/* Admin-only routes */}
            <Route path="/customers" element={
              <RouteGuard requiredRole="admin" fallbackPath="/">
                <Customers />
              </RouteGuard>
            } />
            
            {/* User and Admin routes */}
            <Route path="/dashboard" element={
              <RouteGuard requiredRole="user" fallbackPath="/">
                <Dashboard />
              </RouteGuard>
            } />
            <Route path="/bookings" element={
              <RouteGuard requiredRole="user" fallbackPath="/">
                <Bookings />
              </RouteGuard>
            } />
            
            {/* Auth routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/profile" element={
              <RouteGuard requiredRole="user" fallbackPath="/login">
                <Profile />
              </RouteGuard>
            } />
            <Route path="/chat" element={<Chat />} />
            
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
        <ChatbotButton />
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
