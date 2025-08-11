import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  ShoppingCart,
  Package,
  Calendar,
  DollarSign,
  Trash2,
  ArrowLeft,
  CreditCard,
  Truck,
  CheckCircle,
  Minus,
  Plus,
  X,
} from "lucide-react";
import { products, getProductById } from "@/data/products";
import { useCart } from "@/contexts/CartContext";

const Cart = () => {
  const navigate = useNavigate();
  const { cartItems, removeFromCart, updateQuantity, getCartTotal } = useCart();
  const [couponCode, setCouponCode] = useState("");
  const [appliedCoupon, setAppliedCoupon] = useState("");

  const getProductByIdSafe = (id: number) => {
    return getProductById(id) || {
      id: id,
      name: "Product Not Found",
      description: "This product is no longer available",
      category: "Unknown",
      dailyRate: 0,
      weeklyRate: 0,
      monthlyRate: 0,
      stock: 0,
      totalRentals: 0,
      status: "unavailable",
    };
  };

  const calculateRentalDays = (fromDate: string, toDate: string) => {
    const from = new Date(fromDate);
    const to = new Date(toDate);
    const diffTime = Math.abs(to.getTime() - from.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays || 1;
  };

  const calculateItemTotal = (item: any) => {
    const days = calculateRentalDays(item.fromDate, item.toDate);
    return item.quantity * item.dailyRate * days;
  };



  const applyCoupon = () => {
    if (couponCode.trim()) {
      setAppliedCoupon(couponCode);
      setCouponCode("");
    }
  };

  const removeCoupon = () => {
    setAppliedCoupon("");
  };

  const subtotal = getCartTotal();
  const discount = appliedCoupon ? subtotal * 0.1 : 0; // 10% discount for demo
  const total = subtotal - discount;

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mx-auto mb-6">
              <ShoppingCart className="w-12 h-12 text-muted-foreground" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-4">Your Cart is Empty</h1>
            <p className="text-muted-foreground mb-8 max-w-md mx-auto">
              Looks like you haven't added any items to your cart yet. Start browsing our products to find what you need.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="hero" onClick={() => navigate("/products")}>
                <Package className="w-4 h-4 mr-2" />
                Browse Products
              </Button>
              <Button variant="outline" onClick={() => navigate("/")}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Shopping Cart</h1>
              <p className="text-muted-foreground">Review your rental items and proceed to checkout</p>
            </div>
          </div>
          <Badge variant="secondary" className="text-sm">
            {cartItems.length} {cartItems.length === 1 ? 'item' : 'items'}
          </Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-6">
            {cartItems.map((item) => {
              const product = getProductByIdSafe(item.productId);
              const days = calculateRentalDays(item.fromDate, item.toDate);
              const itemTotal = calculateItemTotal(item);

              return (
                <Card key={item.id} className="shadow-card">
                  <CardContent className="p-6">
                    <div className="flex gap-4">
                      {/* Product Image */}
                      <div className="w-24 h-24 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                        <Package className="w-8 h-8 text-muted-foreground" />
                      </div>

                      {/* Product Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-semibold text-foreground mb-1">{product.name}</h3>
                            <p className="text-sm text-muted-foreground">{product.category}</p>
                          </div>
                                                     <Button
                             variant="ghost"
                             size="sm"
                             onClick={() => removeFromCart(item.id)}
                             className="text-muted-foreground hover:text-destructive"
                           >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>

                        {/* Rental Details */}
                        <div className="grid grid-cols-2 gap-4 mb-4">
                          <div>
                            <p className="text-sm text-muted-foreground mb-1">Rental Period</p>
                            <div className="flex items-center gap-2">
                              <Calendar className="w-4 h-4 text-muted-foreground" />
                              <span className="text-sm font-medium">
                                {new Date(item.fromDate).toLocaleDateString()} - {new Date(item.toDate).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground mb-1">Daily Rate</p>
                            <div className="flex items-center gap-2">
                              <DollarSign className="w-4 h-4 text-muted-foreground" />
                              <span className="text-sm font-medium">${item.dailyRate}</span>
                            </div>
                          </div>
                        </div>

                        {/* Quantity and Price */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-muted-foreground">Quantity:</span>
                            <div className="flex items-center rounded-lg border bg-muted">
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                className="px-2"
                                onClick={() => updateQuantity(item.id, item.quantity - 1)}
                              >
                                <Minus className="w-3 h-3" />
                              </Button>
                              <div className="px-3 py-1 text-sm font-medium">{item.quantity}</div>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                className="px-2"
                                onClick={() => updateQuantity(item.id, item.quantity + 1)}
                              >
                                <Plus className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-muted-foreground">Total for {days} days</p>
                            <p className="text-lg font-semibold text-foreground">${itemTotal}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="shadow-card sticky top-24">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5" />
                  Order Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Coupon Section */}
                <div>
                  <h4 className="font-semibold text-foreground mb-3">Apply Coupon</h4>
                  {appliedCoupon ? (
                    <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg border border-success/20">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-success" />
                        <span className="text-sm font-medium text-success">{appliedCoupon}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={removeCoupon}
                        className="text-muted-foreground hover:text-destructive"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <Input
                        placeholder="Enter coupon code"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value)}
                        className="flex-1"
                      />
                      <Button variant="outline" size="sm" onClick={applyCoupon}>
                        Apply
                      </Button>
                    </div>
                  )}
                </div>

                <Separator />

                {/* Price Breakdown */}
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Subtotal</span>
                    <span className="font-medium">${subtotal}</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-success">
                      <span>Discount</span>
                      <span>-${discount}</span>
                    </div>
                  )}
                  <Separator />
                  <div className="flex justify-between text-lg font-semibold">
                    <span>Total</span>
                    <span>${total}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-3">
                  <Button variant="hero" className="w-full" size="lg">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Proceed to Checkout
                  </Button>
                  <Button variant="outline" className="w-full" onClick={() => navigate("/products")}>
                    <Package className="w-4 h-4 mr-2" />
                    Continue Shopping
                  </Button>
                </div>

                {/* Additional Info */}
                <div className="text-xs text-muted-foreground space-y-2">
                  <div className="flex items-center gap-2">
                    <Truck className="w-3 h-3" />
                    <span>Free delivery on orders over $100</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-3 h-3" />
                    <span>Secure checkout with SSL encryption</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
