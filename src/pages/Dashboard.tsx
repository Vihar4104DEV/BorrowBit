import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  DollarSign, 
  Package, 
  Users, 
  Calendar,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowRight,
  Download,
  Bell
} from "lucide-react";

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // If not authenticated, redirect to login
    if (!isAuthenticated && !isLoading) {
      navigate('/login');
    }
    // Optionally, fetch user/session data here if needed
  }, [isAuthenticated, isLoading, navigate]);
  const stats = [
    {
      title: "Total Revenue",
      value: "$45,231",
      change: "+12.5%",
      trend: "up",
      icon: DollarSign,
      description: "This month"
    },
    {
      title: "Active Rentals",
      value: "23",
      change: "+4",
      trend: "up",
      icon: Package,
      description: "Currently rented"
    },
    {
      title: "Total Customers",
      value: "1,234",
      change: "+8.2%",
      trend: "up",
      icon: Users,
      description: "All time"
    },
    {
      title: "Bookings Today",
      value: "12",
      change: "-2",
      trend: "down",
      icon: Calendar,
      description: "New bookings"
    }
  ];

  const recentBookings = [
    {
      id: "BK001",
      customer: "John Smith",
      product: "Professional Camera Kit",
      status: "confirmed",
      amount: "$450",
      startDate: "2024-01-15",
      endDate: "2024-01-18"
    },
    {
      id: "BK002",
      customer: "Sarah Johnson",
      product: "Wedding Tent Large",
      status: "pending",
      amount: "$1,200",
      startDate: "2024-01-20",
      endDate: "2024-01-22"
    },
    {
      id: "BK003",
      customer: "Mike Wilson",
      product: "Sound System Pro",
      status: "active",
      amount: "$900",
      startDate: "2024-01-12",
      endDate: "2024-01-19"
    },
    {
      id: "BK004",
      customer: "Emily Davis",
      product: "Luxury Car BMW X5",
      status: "overdue",
      amount: "$540",
      startDate: "2024-01-10",
      endDate: "2024-01-13"
    }
  ];

  const topProducts = [
    {
      name: "Construction Tools Set",
      rentals: 89,
      revenue: "$12,340",
      category: "Tools & Equipment"
    },
    {
      name: "Party Lighting Package",
      rentals: 156,
      revenue: "$18,720",
      category: "Event Equipment"
    },
    {
      name: "Sound System Pro",
      rentals: 67,
      revenue: "$20,100",
      category: "Audio"
    },
    {
      name: "Professional Camera Kit",
      rentals: 48,
      revenue: "$14,400",
      category: "Photography"
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "confirmed":
        return <Badge className="bg-success text-success-foreground"><CheckCircle className="w-3 h-3 mr-1" />Confirmed</Badge>;
      case "pending":
        return <Badge className="bg-warning text-warning-foreground"><Clock className="w-3 h-3 mr-1" />Pending</Badge>;
      case "active":
        return <Badge className="bg-primary text-primary-foreground"><Calendar className="w-3 h-3 mr-1" />Active</Badge>;
      case "overdue":
        return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Overdue</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's what's happening with your rental business.</p>
          </div>
          <div className="flex gap-3 mt-4 sm:mt-0">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
            <Button variant="hero">
              <Bell className="w-4 h-4 mr-2" />
              View Notifications
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            const isPositive = stat.trend === "up";
            return (
              <Card key={index} className="shadow-card hover:shadow-elegant transition-smooth">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <div className="w-12 h-12 gradient-primary rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-primary-foreground" />
                    </div>
                    <div className={`flex items-center text-sm ${
                      isPositive ? "text-success" : "text-destructive"
                    }`}>
                      {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                      {stat.change}
                    </div>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-foreground mb-1">{stat.value}</p>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Recent Bookings */}
          <Card className="shadow-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-xl font-semibold">Recent Bookings</CardTitle>
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentBookings.map((booking) => (
                <div key={booking.id} className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-smooth">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-foreground">{booking.customer}</p>
                      {getStatusBadge(booking.status)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">{booking.product}</p>
                    <p className="text-xs text-muted-foreground">
                      {booking.startDate} - {booking.endDate}
                    </p>
                  </div>
                  <div className="text-right ml-4">
                    <p className="font-semibold text-foreground">{booking.amount}</p>
                    <p className="text-xs text-muted-foreground">{booking.id}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Top Products */}
          <Card className="shadow-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-xl font-semibold">Top Performing Products</CardTitle>
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {topProducts.map((product, index) => (
                <div key={index} className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-smooth">
                  <div className="flex-1">
                    <p className="font-semibold text-foreground mb-1">{product.name}</p>
                    <p className="text-sm text-muted-foreground">{product.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-foreground">{product.revenue}</p>
                    <p className="text-sm text-muted-foreground">{product.rentals} rentals</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-xl font-semibold">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center" onClick={() => navigate('/products/create')}>
                <Package className="w-6 h-6 mb-2" />
                <span>Add Product</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center" onClick={() => navigate('/bookings/create')}>
                <Calendar className="w-6 h-6 mb-2" />
                <span>New Booking</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center" onClick={() => navigate('/customers/create')}>
                <Users className="w-6 h-6 mb-2" />
                <span>Add Customer</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center" onClick={() => navigate('/invoices/create')}>
                <DollarSign className="w-6 h-6 mb-2" />
                <span>Generate Invoice</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;