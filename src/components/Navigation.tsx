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

  // Update nav item type to support children
  type NavItem = {
    href?: string;
    label: string;
    icon?: any;
    children?: Array<{ href: string; label: string; icon?: any }>;
  };

  // Define navigation items based on authentication status and user role
  const getNavItems = () => {
    const baseItems: NavItem[] = [
      { href: "/", label: "Home" },
      { href: "/products", label: "Products", icon: Package },
    ];

    if (isAuthenticated) {
      // Add user-specific items
      let userItems: NavItem[] = [
        { href: "/bookings", label: "Bookings", icon: Calendar },
        { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
        { href: "/cart", label: "Cart", icon: Package },
      ];

      // Add admin-specific items, but group them under a dropdown if too many
      const isAdmin = user?.user_role?.includes('ADMIN') || user?.user_role?.includes('SUPER_ADMIN');
      if (isAdmin) {
        userItems.push({
          label: "Admin",
          icon: Users,
          children: [
            { href: "/customers", label: "Customers", icon: Users },
            { href: "/delivery-partner", label: "Delivery Partner", icon: Users },
          ],
        });
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
              if (item.children && item.children.length > 0) {
                // Render dropdown for admin items
                return (
                  <div key={item.label} className="relative group">
                    <Button variant="outline" size="sm" className="flex items-center">
                      {item.icon && <item.icon className="w-4 h-4 mr-2" />}
                      {item.label}
                      <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                    </Button>
                    <div className="absolute left-0 mt-2 w-48 bg-background border border-border rounded-lg shadow-lg z-10 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity">
                      {item.children.map((child) => (
                        <Link
                          key={child.href}
                          to={child.href}
                          className={`flex items-center px-4 py-2 text-sm rounded-md hover:bg-muted transition-smooth`}
                        >
                          {child.icon && <child.icon className="w-4 h-4 mr-2" />}
                          {child.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              }
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