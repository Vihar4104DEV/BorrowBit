import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, 
  Filter, 
  Calendar, 
  Clock,
  CheckCircle,
  AlertCircle,
  Eye,
  Edit,
  Plus,
  DollarSign,
  User,
  Package,
  FileText,
  Send
} from "lucide-react";

const Bookings = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const navigate = useNavigate();
  
  const bookings = [
    {
      id: "BK001",
      customer: "John Smith",
      email: "john.smith@email.com",
      phone: "+1 234 567 8900",
      product: "Professional Camera Kit",
      category: "Photography",
      status: "confirmed",
      amount: 450,
      deposit: 100,
      startDate: "2024-01-15",
      endDate: "2024-01-18",
      duration: "3 days",
      createdDate: "2024-01-10",
      notes: "Wedding photography event"
    },
    {
      id: "BK002",
      customer: "Sarah Johnson",
      email: "sarah.johnson@email.com",
      phone: "+1 234 567 8901",
      product: "Wedding Tent Large",
      category: "Event Equipment",
      status: "pending",
      amount: 1200,
      deposit: 300,
      startDate: "2024-01-20",
      endDate: "2024-01-22",
      duration: "2 days",
      createdDate: "2024-01-12",
      notes: "Outdoor wedding ceremony"
    },
    {
      id: "BK003",
      customer: "Mike Wilson",
      email: "mike.wilson@email.com",
      phone: "+1 234 567 8902",
      product: "Sound System Pro",
      category: "Audio",
      status: "active",
      amount: 900,
      deposit: 200,
      startDate: "2024-01-12",
      endDate: "2024-01-19",
      duration: "7 days",
      createdDate: "2024-01-08",
      notes: "Corporate event"
    },
    {
      id: "BK004",
      customer: "Emily Davis",
      email: "emily.davis@email.com",
      phone: "+1 234 567 8903",
      product: "Luxury Car BMW X5",
      category: "Vehicles",
      status: "overdue",
      amount: 540,
      deposit: 150,
      startDate: "2024-01-10",
      endDate: "2024-01-13",
      duration: "3 days",
      createdDate: "2024-01-05",
      notes: "Business trip rental"
    },
    {
      id: "BK005",
      customer: "David Brown",
      email: "david.brown@email.com",
      phone: "+1 234 567 8904",
      product: "Construction Tools Set",
      category: "Tools & Equipment",
      status: "completed",
      amount: 225,
      deposit: 75,
      startDate: "2024-01-05",
      endDate: "2024-01-08",
      duration: "3 days",
      createdDate: "2024-01-02",
      notes: "Home renovation project"
    },
    {
      id: "BK006",
      customer: "Lisa Anderson",
      email: "lisa.anderson@email.com",
      phone: "+1 234 567 8905",
      product: "Party Lighting Package",
      category: "Event Equipment",
      status: "cancelled",
      amount: 360,
      deposit: 90,
      startDate: "2024-01-25",
      endDate: "2024-01-26",
      duration: "1 day",
      createdDate: "2024-01-13",
      notes: "Birthday party (cancelled due to weather)"
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
      case "completed":
        return <Badge className="bg-muted text-muted-foreground"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>;
      case "cancelled":
        return <Badge variant="destructive">Cancelled</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getFilteredBookings = (filter: string) => {
    let filtered = bookings;
    
    if (filter !== "all") {
      filtered = bookings.filter(booking => booking.status === filter);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(booking =>
        booking.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
        booking.product.toLowerCase().includes(searchTerm.toLowerCase()) ||
        booking.id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered;
  };

  const getStatusCount = (status: string) => {
    if (status === "all") return bookings.length;
    return bookings.filter(booking => booking.status === status).length;
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Bookings Management</h1>
            <p className="text-muted-foreground">Track and manage all rental bookings</p>
          </div>
          {/* <Button variant="hero" size="lg" className="mt-4 sm:mt-0">
            <Plus className="w-4 h-4 mr-2" />
            Create New Booking
          </Button> */}
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search bookings, customers, products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 shadow-card"
            />
          </div>
          <Button variant="outline" className="shadow-card">
            <Filter className="w-4 h-4 mr-2" />
            Advanced Filters
          </Button>
        </div>

        {/* Status Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-10 sm:mt-10">
          <TabsList className="grid w-full grid-cols-3 lg:grid-cols-7 sm:grid-cols-12 shadow-card">
            <TabsTrigger value="all" className="text-sm">
              All ({getStatusCount("all")})
            </TabsTrigger>
            <TabsTrigger value="pending" className="text-sm">
              Pending ({getStatusCount("pending")})
            </TabsTrigger>
            <TabsTrigger value="confirmed" className="text-sm">
              Confirmed ({getStatusCount("confirmed")})
            </TabsTrigger>
            <TabsTrigger value="active" className="text-sm">
              Active ({getStatusCount("active")})
            </TabsTrigger>
            <TabsTrigger value="overdue" className="text-sm">
              Overdue ({getStatusCount("overdue")})
            </TabsTrigger>
            <TabsTrigger value="completed" className="text-sm">
              Completed ({getStatusCount("completed")})
            </TabsTrigger>
            <TabsTrigger value="cancelled" className="text-sm">
              Cancelled ({getStatusCount("cancelled")})
            </TabsTrigger>
          </TabsList>

          {["all", "pending", "confirmed", "active", "overdue", "completed", "cancelled"].map((tab) => (
            <TabsContent key={tab} value={tab} className="space-y-6">
              <div className="grid gap-6">
                {getFilteredBookings(tab).map((booking) => (
                  <Card key={booking.id} className="shadow-card hover:shadow-elegant transition-smooth">
                    <CardHeader className="pb-3">
                      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                        <div className="flex items-center gap-4 mb-4 lg:mb-0">
                          <div className="w-12 h-12 gradient-primary rounded-lg flex items-center justify-center">
                            <Calendar className="w-6 h-6 text-primary-foreground" />
                          </div>
                          <div>
                            <CardTitle className="text-lg font-semibold text-foreground">
                              {booking.id} - {booking.customer}
                            </CardTitle>
                            <p className="text-sm text-muted-foreground">
                              {booking.product} • {booking.duration}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          {getStatusBadge(booking.status)}
                          <span className="text-lg font-bold text-foreground">${booking.amount}</span>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                        {/* Customer Info */}
                        <div className="space-y-2">
                          <h4 className="text-sm font-semibold text-foreground flex items-center">
                            <User className="w-4 h-4 mr-1" />
                            Customer
                          </h4>
                          <p className="text-sm text-muted-foreground">{booking.email}</p>
                          <p className="text-sm text-muted-foreground">{booking.phone}</p>
                        </div>

                        {/* Product Info */}
                        <div className="space-y-2">
                          <h4 className="text-sm font-semibold text-foreground flex items-center">
                            <Package className="w-4 h-4 mr-1" />
                            Product
                          </h4>
                          <p className="text-sm text-muted-foreground">{booking.category}</p>
                          <p className="text-sm text-muted-foreground">Deposit: ${booking.deposit}</p>
                        </div>

                        {/* Dates */}
                        <div className="space-y-2">
                          <h4 className="text-sm font-semibold text-foreground flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            Rental Period
                          </h4>
                          <p className="text-sm text-muted-foreground">Start: {booking.startDate}</p>
                          <p className="text-sm text-muted-foreground">End: {booking.endDate}</p>
                        </div>

                        {/* Financial */}
                        <div className="space-y-2">
                          <h4 className="text-sm font-semibold text-foreground flex items-center">
                            <DollarSign className="w-4 h-4 mr-1" />
                            Financial
                          </h4>
                          <p className="text-sm text-muted-foreground">Total: ${booking.amount}</p>
                          <p className="text-sm text-muted-foreground">Created: {booking.createdDate}</p>
                        </div>
                      </div>

                      {/* Notes */}
                      {booking.notes && (
                        <div className="p-3 bg-muted rounded-lg mb-4">
                          <p className="text-sm text-muted-foreground">
                            <strong>Notes:</strong> {booking.notes}
                          </p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex flex-wrap gap-2">
                        <Button variant="outline" size="sm" onClick={() => navigate(`/bookings/${booking.id}`)}>
                          <Eye className="w-4 h-4 mr-1" />
                          View Details
                        </Button>
                        <Button variant="default" size="sm" onClick={() => navigate(`/bookings/edit/${booking.id}`)}>
                          <Edit className="w-4 h-4 mr-1" />
                          Edit Booking
                        </Button>
                        <Button variant="success" size="sm" onClick={() => alert(`Contract generated for booking ${booking.id}`)}>
                          <FileText className="w-4 h-4 mr-1" />
                          Generate Contract
                        </Button>
                        <Button variant="hero" size="sm" onClick={() => alert(`Notification sent for booking ${booking.id}`)}>
                          <Send className="w-4 h-4 mr-1" />
                          Send Notification
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                {getFilteredBookings(tab).length === 0 && (
                  <Card className="shadow-card">
                    <CardContent className="py-12 text-center">
                      <Package className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-foreground mb-2">No bookings found</h3>
                      <p className="text-muted-foreground mb-4">
                        {searchTerm 
                          ? "No bookings match your search criteria" 
                          : `No ${tab === "all" ? "" : tab} bookings at the moment`
                        }
                      </p>
                      <Button variant="hero" onClick={() => navigate("/bookings/create") }>
                        <Plus className="w-4 h-4 mr-2" />
                        Create New Booking
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  );
};

export default Bookings;