import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X, Calendar, Package, Users, BarChart3, MessageCircle, LogOut, TestTube } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  // Define navigation items based on authentication status and user role
  const getNavItems = () => {
    const baseItems = [
      { href: "/", label: "Home" },
      { href: "/products", label: "Products", icon: Package },
    ];

    if (isAuthenticated) {
      // Add user-specific items
      const userItems = [
        { href: "/bookings", label: "Bookings", icon: Calendar },
        { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
      ];

      // Add admin-specific items
      const isAdmin = user?.user_role?.includes('admin');
if (isAdmin) {
  userItems.push({ href: "/customers", label: "Customers", icon: Users });
}


      return [...baseItems, ...userItems];
    } else {
      // Guest sees only home and products
      return baseItems;
    }
  };

  const navItems = getNavItems();

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <nav className="bg-background/95 backdrop-blur-md border-b border-border shadow-card sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center">
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
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-smooth ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-elegant"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  {Icon && <Icon className="w-4 h-4 mr-2" />}
                  {item.label}
                </Link>
              );
            })}
            
            {/* API Test Link - Always visible for debugging */}
            {/* <Link
              to="/api-test"
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-smooth ${
                location.pathname === '/api-test'
                  ? "bg-orange-500 text-white shadow-elegant"
                  : "text-orange-600 hover:text-orange-700 hover:bg-orange-50"
              }`}
            >
              <TestTube className="w-4 h-4 mr-2" />
              API Test
            </Link> */}
          </div>

          {/* Action Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <span className="text-sm text-muted-foreground">
                  Welcome, {user?.first_name || user?.email?.split('@')[0]}!
                  {user?.user_role && (
                    <span className="ml-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                      {user.user_role}
                    </span>
                  )}
                </span>
                <Button variant="outline" size="sm" onClick={() => navigate("/profile")}>
                  Profile
                </Button>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </div>
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
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-smooth ${
                      isActive
                        ? "bg-primary text-primary-foreground shadow-elegant"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    {Icon && <Icon className="w-4 h-4 mr-2" />}
                    {item.label}
                  </Link>
                );
              })}
              
              {/* API Test Link in mobile menu */}
              <Link
                to="/api-test"
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-smooth ${
                  location.pathname === '/api-test'
                    ? "bg-orange-500 text-white shadow-elegant"
                    : "text-orange-600 hover:text-orange-700 hover:bg-orange-50"
                }`}
                onClick={() => setIsOpen(false)}
              >
                <TestTube className="w-4 h-4 mr-2" />
                API Test
              </Link>
              
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => { setIsOpen(false); navigate("/chat"); }}
              >
                <MessageCircle className="w-4 h-4 mr-2" /> Chatbot
              </Button>
              <div className="pt-4 space-y-2">
                {isAuthenticated ? (
                  <>
                    <div className="px-3 py-2 text-sm text-muted-foreground">
                      Welcome, {user?.first_name || user?.email?.split('@')[0]}!
                      {user?.user_role && (
                        <span className="ml-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                          {user.user_role}
                        </span>
                      )}
                    </div>
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => { setIsOpen(false); navigate("/profile"); }}
                    >
                      Profile
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => { setIsOpen(false); handleLogout(); }}
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
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