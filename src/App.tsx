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
import DeliveryPartner from "./pages/DeliveryPartner";
import Cart from "./pages/Cart";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Profile from "./pages/Profile";
import { AuthProvider } from "@/contexts/AuthContext";
import { CartProvider } from "@/contexts/CartContext";
import { ChatbotButton } from "@/components/ChatbotButton";
import Chat from "@/pages/Chat";
import ProductDetail from "@/pages/ProductDetail";
import AddProduct from "@/pages/AddProduct";
import { RouteGuard } from "@/components/RouteGuard";
import MyProducts from "./pages/MyProducts";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <CartProvider>
          <BrowserRouter>
            <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/products" element={<Products />} />
            <Route path="/my-products" element={
              <RouteGuard requiredRole="user" fallbackPath="/">
                <MyProducts />
              </RouteGuard>
            } />
            <Route path="/products/:id" element={
              <RouteGuard requiredRole="user" fallbackPath="/">
                <ProductDetail />
              </RouteGuard>
            } />
            <Route path="/add-product" element={<AddProduct />} />
            
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
            
            {/* Delivery Partner route */}
            <Route path="/delivery-partner" element={
              <RouteGuard requiredRole="delivery" fallbackPath="/">
                <DeliveryPartner />
              </RouteGuard>
            } />
            
            {/* Cart route */}
            <Route path="/cart" element={
              <RouteGuard requiredRole="user" fallbackPath="/login">
                <Cart />
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
        </CartProvider>
        </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
