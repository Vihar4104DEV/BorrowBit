import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Menu, X, Calendar, Package, Users, BarChart3, MessageCircle, Truck, ShoppingCart } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useCart } from "@/contexts/CartContext";

export const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAdmin, isUser, isDelivery } = useAuth();
  const { getCartItemCount } = useCart();

  // Debug logging for role detection
  console.log("Navigation - User role debug:", { 
    isAdmin, 
    isUser, 
    isDelivery, 
    userRole: user?.role 
  });

  // Define navigation item type
  type NavItem = {
    href: string;
    label: string;
    icon?: any;
    badge?: number;
  };

  // Define navigation items based on user role
  const getNavItems = (): NavItem[] => {
    const baseItems = [
      { href: "/", label: "Home" },
      { href: "/products", label: "Products", icon: Package },
    ];

    if (isAdmin) {
      // Admin sees everything except cart (cart is in action buttons)
      return [
        ...baseItems,
        { href: "/bookings", label: "Bookings", icon: Calendar },
        { href: "/customers", label: "Customers", icon: Users },
        { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
      ];
    } else if (isDelivery) {
      // Delivery partner sees only home and delivery dashboard
      return [
        { href: "/", label: "Home" },
        { href: "/delivery-partner", label: "Delivery Dashboard", icon: Truck },
      ];
    } else if (isUser) {
      // Normal user sees limited items
      return [
        { href: "/", label: "Home" },
        { href: "/products", label: "Products", icon: Package },
        { href: "/bookings", label: "Bookings", icon: Calendar },
        { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
        { href: "/my-products", label: "My Products", icon: Package },
      ];
    } else {
      // Guest sees only home and products
      return baseItems;
    }
  };

  const navItems = getNavItems();

  // Debug logging for navigation items
  console.log("Navigation - Generated nav items:", navItems);
  console.log("Navigation - Current user role:", user?.role);
  console.log("Navigation - isDelivery flag:", isDelivery);

  return (
    <nav className="bg-background/95 backdrop-blur-md border-b border-border shadow-card sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center">
              {/* <Calendar className="w-5 h-5 text-primary-foreground" /> */}
              <img src="/logo.png" alt="Icon" className="w-7 h-7 text-primary-foreground" />

            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Borrowbit
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-smooth relative ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-elegant"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  {Icon && <Icon className="w-4 h-4 mr-2" />}
                  {item.label}
                  {item.badge && item.badge > 0 && (
                    <Badge variant="destructive" className="ml-2 h-5 w-5 rounded-full p-0 text-xs">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              );
            })}
            {/* <Button
              variant="ghost"
              size="sm"
              className="ml-1"
              onClick={() => navigate("/chat")}
            >
              <MessageCircle className="w-4 h-4 mr-2" /> Chatbot
            </Button> */}
          </div>

          {/* Action Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            {user ? (
              <>
                {/* Only show cart for non-delivery users */}
                {!isDelivery && (
                  <Button variant="outline" size="sm" onClick={() => navigate("/cart")} className="flex items-center gap-2">
                    <ShoppingCart className="w-4 h-4" />
                    Cart
                    {getCartItemCount() > 0 && (
                      <Badge variant="destructive" className="h-5 w-5 rounded-full p-0 text-xs">
                        {getCartItemCount()}
                      </Badge>
                    )}
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={() => navigate("/profile")} className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Profile
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" size="sm" onClick={() => navigate("/login")}> 
                  Login
                </Button>
                <Button variant="hero" size="sm" onClick={() => navigate("/signup")}> 
                  Get Started
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden pb-4 animate-slide-up">
            <div className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-smooth relative ${
                      isActive
                        ? "bg-primary text-primary-foreground shadow-elegant"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    {Icon && <Icon className="w-4 h-4 mr-2" />}
                    {item.label}
                    {item.badge && item.badge > 0 && (
                      <Badge variant="destructive" className="ml-2 h-5 w-5 rounded-full p-0 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </Link>
                );
              })}
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => { setIsOpen(false); navigate("/chat"); }}
              >
                <MessageCircle className="w-4 h-4 mr-2" /> Chatbot
              </Button>
              <div className="pt-4 space-y-2">
                {user ? (
                  <>
                    {/* Only show cart for non-delivery users */}
                    {!isDelivery && (
                      <Button
                        variant="outline"
                        className="w-full justify-start"
                        onClick={() => { setIsOpen(false); navigate("/cart"); }}
                      >
                        <ShoppingCart className="w-4 h-4" />
                        Cart
                        {getCartItemCount() > 0 && (
                          <Badge variant="destructive" className="ml-2 h-5 w-5 rounded-full p-0 text-xs">
                            {getCartItemCount()}
                          </Badge>
                        )}
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => { setIsOpen(false); navigate("/profile"); }}
                    >
                      <Users className="w-4 h-4" />
                      Profile
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => { setIsOpen(false); navigate("/login"); }}
                    >
                      Login
                    </Button>
                    <Button
                      variant="hero"
                      className="w-full justify-start"
                      onClick={() => { setIsOpen(false); navigate("/signup"); }}
                    >
                      Get Started
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};