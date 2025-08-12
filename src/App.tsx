import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Products from "./pages/Products";
import Dashboard from "./pages/Dashboard";
import Bookings from "./pages/Bookings";
import GenerateContract from "./pages/GenerateContract";
import SendNotification from "./pages/SendNotification";
import AdvancedFilters from "./pages/AdvancedFilters";
import BookingDetail from "./pages/BookingDetail";
import EditBooking from "./pages/EditBooking";
import CreateBooking from "./pages/CreateBooking";
import Customers from "./pages/Customers";
import DeliveryPartner from "./pages/DeliveryPartner";
import Cart from "./pages/Cart";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Profile from "./pages/Profile";
import VerifyOtp from "./pages/VerifyOtp";
import { ChatbotButton } from "@/components/ChatbotButton";
import Chat from "@/pages/Chat";
import ProductDetail from "@/pages/ProductDetail";
import CreateProduct from "@/pages/CreateProduct";
import EditProduct from "@/pages/EditProduct";
import ProtectedRoute from "@/components/ProtectedRoute";
import ApiTest from "@/components/ApiTest";

import { CartProvider } from "@/contexts/CartContext";
const App = () => (
  <TooltipProvider>
  <CartProvider>
    <TooltipProvider>
    <Sonner />
    <BrowserRouter>
      <Routes>
        <Route path="/bookings/contract/:id" element={
          <ProtectedRoute>
            <GenerateContract />
          </ProtectedRoute>
        } />
        <Route path="/bookings/notify/:id" element={
          <ProtectedRoute>
            <SendNotification />
          </ProtectedRoute>
        } />
        <Route path="/bookings/filters" element={
          <ProtectedRoute>
            <AdvancedFilters />
          </ProtectedRoute>
        } />
        <Route path="/" element={<Index />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/products/create" element={<CreateProduct />} />
        <Route path="/products/edit/:id" element={<EditProduct />} />
        
        {/* API Test Route */}
        {/* <Route path="/api-test" element={<ApiTest />} /> */}
        
        {/* Admin-only routes */}
        <Route path="/customers" element={
          <ProtectedRoute>
            <Customers />
          </ProtectedRoute>
        } />
        
        {/* User and Admin routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
         <Route path="/delivery-partner" element={
              <ProtectedRoute>
                <DeliveryPartner />
             </ProtectedRoute>
            } />
            
            {/* Cart route */}
            <Route path="/cart" element={
              <ProtectedRoute>
                <Cart />
            </ProtectedRoute>
            } />
        <Route path="/bookings" element={
          <ProtectedRoute>
            <Bookings />
          </ProtectedRoute>
        } />
        <Route path="/bookings/:id" element={
          <ProtectedRoute>
            <BookingDetail />
          </ProtectedRoute>
        } />
        <Route path="/bookings/edit/:id" element={
          <ProtectedRoute>
            <EditBooking />
          </ProtectedRoute>
        } />
        <Route path="/bookings/create" element={
          <ProtectedRoute>
            <CreateBooking />
          </ProtectedRoute>
        } />
        
        {/* Auth routes */}
        <Route path="/login" element={
          <ProtectedRoute requireAuth={false}>
            <Login />
          </ProtectedRoute>
        } />
        <Route path="/signup" element={
          <ProtectedRoute requireAuth={false}>
            <Signup />
          </ProtectedRoute>
        } />
        <Route path="/verify-otp" element={<VerifyOtp />} />
        <Route path="/profile" element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        } />
        <Route path="/chat" element={<Chat />} />
        
        {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
    <ChatbotButton />
    <ChatbotButton />
    </TooltipProvider>
  </CartProvider>
  </TooltipProvider>
);

export default App;
