import { useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Search, 
  Filter, 
  Users, 
  Phone,
  Mail,
  Calendar,
  DollarSign,
  Star,
  Eye,
  Edit,
  Plus,
  MapPin,
  CreditCard,
  Package
} from "lucide-react";

const Customers = () => {
  const [searchTerm, setSearchTerm] = useState("");
  
  const customers = [
    {
      id: 1,
      name: "John Smith",
      email: "john.smith@email.com",
      phone: "+1 234 567 8900",
      address: "123 Main St, New York, NY 10001",
      joinDate: "2023-06-15",
      totalBookings: 12,
      totalSpent: 4250,
      activeRentals: 1,
      status: "active",
      tier: "gold",
      lastBooking: "2024-01-15",
      rating: 4.8,
      notes: "Preferred customer, always pays on time"
    },
    {
      id: 2,
      name: "Sarah Johnson",
      email: "sarah.johnson@email.com",
      phone: "+1 234 567 8901",
      address: "456 Oak Ave, Los Angeles, CA 90210",
      joinDate: "2023-09-22",
      totalBookings: 8,
      totalSpent: 2890,
      activeRentals: 0,
      status: "active",
      tier: "silver",
      lastBooking: "2024-01-12",
      rating: 4.6,
      notes: "Wedding planner, books event equipment regularly"
    },
    {
      id: 3,
      name: "Mike Wilson",
      email: "mike.wilson@email.com",
      phone: "+1 234 567 8902",
      address: "789 Pine Rd, Chicago, IL 60601",
      joinDate: "2023-12-03",
      totalBookings: 15,
      totalSpent: 6750,
      activeRentals: 2,
      status: "active",
      tier: "platinum",
      lastBooking: "2024-01-10",
      rating: 4.9,
      notes: "Corporate client, bulk bookings for events"
    },
    {
      id: 4,
      name: "Emily Davis",
      email: "emily.davis@email.com",
      phone: "+1 234 567 8903",
      address: "321 Elm St, Miami, FL 33101",
      joinDate: "2023-04-18",
      totalBookings: 3,
      totalSpent: 890,
      activeRentals: 0,
      status: "inactive",
      tier: "bronze",
      lastBooking: "2023-11-22",
      rating: 4.2,
      notes: "Casual renter, mainly weekend bookings"
    },
    {
      id: 5,
      name: "David Brown",
      email: "david.brown@email.com",
      phone: "+1 234 567 8904",
      address: "654 Maple Dr, Austin, TX 78701",
      joinDate: "2023-08-10",
      totalBookings: 6,
      totalSpent: 1650,
      activeRentals: 0,
      status: "active",
      tier: "silver",
      lastBooking: "2024-01-08",
      rating: 4.4,
      notes: "Construction contractor, tools and equipment rentals"
    },
    {
      id: 6,
      name: "Lisa Anderson",
      email: "lisa.anderson@email.com",
      phone: "+1 234 567 8905",
      address: "987 Cedar Ln, Seattle, WA 98101",
      joinDate: "2023-11-05",
      totalBookings: 4,
      totalSpent: 1200,
      activeRentals: 0,
      status: "active",
      tier: "bronze",
      lastBooking: "2023-12-30",
      rating: 4.1,
      notes: "Event organizer, seasonal bookings"
    }
  ];

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case "platinum":
        return <Badge className="bg-gradient-to-r from-gray-400 to-gray-600 text-white">Platinum</Badge>;
      case "gold":
        return <Badge className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white">Gold</Badge>;
      case "silver":
        return <Badge className="bg-gradient-to-r from-gray-300 to-gray-500 text-white">Silver</Badge>;
      case "bronze":
        return <Badge className="bg-gradient-to-r from-orange-400 to-orange-600 text-white">Bronze</Badge>;
      default:
        return <Badge variant="secondary">{tier}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-success text-success-foreground">Active</Badge>;
      case "inactive":
        return <Badge variant="secondary">Inactive</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm)
  );

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating) 
            ? "text-yellow-400 fill-current" 
            : "text-gray-300"
        }`}
      />
    ));
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Customer Management</h1>
            <p className="text-muted-foreground">Manage your customer relationships and rental history</p>
          </div>
          <Button variant="hero" size="lg" className="mt-4 sm:mt-0">
            <Plus className="w-4 h-4 mr-2" />
            Add New Customer
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search customers by name, email, or phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 shadow-card"
            />
          </div>
          <Button variant="outline" className="shadow-card">
            <Filter className="w-4 h-4 mr-2" />
            Filter & Sort
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Total Customers</p>
                  <p className="text-2xl font-bold text-foreground">{customers.length}</p>
                </div>
                <Users className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Active Customers</p>
                  <p className="text-2xl font-bold text-success">
                    {customers.filter(c => c.status === "active").length}
                  </p>
                </div>
                <Users className="w-8 h-8 text-success" />
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Total Revenue</p>
                  <p className="text-2xl font-bold text-foreground">
                    ${customers.reduce((sum, c) => sum + c.totalSpent, 0).toLocaleString()}
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Avg Rating</p>
                  <p className="text-2xl font-bold text-foreground">
                    {(customers.reduce((sum, c) => sum + c.rating, 0) / customers.length).toFixed(1)}
                  </p>
                </div>
                <Star className="w-8 h-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Customers Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredCustomers.map((customer) => (
            <Card key={customer.id} className="shadow-card hover:shadow-elegant transition-smooth">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6 text-primary-foreground" />
                      </div>
                      <div>
                        <CardTitle className="text-lg font-semibold text-foreground">
                          {customer.name}
                        </CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          {getTierBadge(customer.tier)}
                          {getStatusBadge(customer.status)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center justify-end mb-1">
                      {renderStars(customer.rating)}
                      <span className="ml-2 text-sm text-muted-foreground">{customer.rating}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Customer #{customer.id}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Contact Information */}
                <div className="space-y-2">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Mail className="w-4 h-4 mr-2" />
                    {customer.email}
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Phone className="w-4 h-4 mr-2" />
                    {customer.phone}
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="w-4 h-4 mr-2" />
                    {customer.address}
                  </div>
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-2 gap-4 p-3 bg-muted rounded-lg">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Total Bookings</p>
                    <p className="text-xl font-bold text-foreground">{customer.totalBookings}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Total Spent</p>
                    <p className="text-xl font-bold text-foreground">${customer.totalSpent.toLocaleString()}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Join Date</p>
                    <p className="text-sm font-medium text-foreground">{customer.joinDate}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Booking</p>
                    <p className="text-sm font-medium text-foreground">{customer.lastBooking}</p>
                  </div>
                </div>

                {customer.activeRentals > 0 && (
                  <div className="p-3 bg-primary/10 rounded-lg">
                    <div className="flex items-center text-primary">
                      <Package className="w-4 h-4 mr-2" />
                      <span className="text-sm font-medium">
                        {customer.activeRentals} Active Rental{customer.activeRentals > 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                )}

                {/* Notes */}
                {customer.notes && (
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      <strong>Notes:</strong> {customer.notes}
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="w-4 h-4 mr-1" />
                    View Profile
                  </Button>
                  <Button variant="default" size="sm" className="flex-1">
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button variant="hero" size="sm" className="flex-1">
                    <Calendar className="w-4 h-4 mr-1" />
                    New Booking
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredCustomers.length === 0 && (
          <Card className="shadow-card">
            <CardContent className="py-12 text-center">
              <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">No customers found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm 
                  ? "No customers match your search criteria" 
                  : "Start building your customer base"
                }
              </p>
              <Button variant="hero">
                <Plus className="w-4 h-4 mr-2" />
                Add First Customer
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Customers;