import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
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
  Package,
  Ban,
  UserCheck
} from "lucide-react";

const Customers = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isViewProfileDialogOpen, setIsViewProfileDialogOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [editForm, setEditForm] = useState({
    name: "",
    email: "",
    phone: "",
    role: "user"
  });

  // Debug useEffect to monitor state changes
  useEffect(() => {
    console.log("State changed - Dialog open:", isViewProfileDialogOpen, "Selected customer:", selectedCustomer);
  }, [isViewProfileDialogOpen, selectedCustomer]);
  
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
      notes: "Preferred customer, always pays on time",
      role: "user",
      isBanned: false
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
      notes: "Wedding planner, books event equipment regularly",
      role: "user",
      isBanned: false
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
      notes: "Corporate client, bulk bookings for events",
      role: "user",
      isBanned: false
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
      notes: "Casual renter, mainly weekend bookings",
      role: "user",
      isBanned: false
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
      notes: "Small business owner, equipment rentals",
      role: "user",
      isBanned: false
    }
  ];

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm)
  );

  const handleViewProfile = (customer: any) => {
    console.log("View Profile clicked for customer:", customer);
    console.log("Current dialog state:", isViewProfileDialogOpen);
    setSelectedCustomer(customer);
    setIsViewProfileDialogOpen(true);
    console.log("Dialog state set to true");
  };

  const handleEditCustomer = (customer: any) => {
    setSelectedCustomer(customer);
    setEditForm({
      name: customer.name,
      email: customer.email,
      phone: customer.phone,
      role: customer.role
    });
    setIsEditDialogOpen(true);
  };

  const handleSaveEdit = () => {
    if (selectedCustomer) {
      const customerIndex = customers.findIndex(c => c.id === selectedCustomer.id);
      if (customerIndex !== -1) {
        customers[customerIndex] = {
          ...customers[customerIndex],
          ...editForm
        };
      }
    }
    setIsEditDialogOpen(false);
    setSelectedCustomer(null);
  };

  const handleBanCustomer = (customer: any) => {
    const customerIndex = customers.findIndex(c => c.id === customer.id);
    if (customerIndex !== -1) {
      customers[customerIndex].isBanned = !customers[customerIndex].isBanned;
      customers[customerIndex].status = customers[customerIndex].isBanned ? "banned" : "active";
    }
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "admin":
        return <Badge className="bg-destructive text-destructive-foreground">Admin</Badge>;
      case "user":
        return <Badge className="bg-primary text-primary-foreground">User</Badge>;
      case "delivery":
        return <Badge className="bg-outline text-outline-foreground">Delivery</Badge>;
      default:
        return <Badge variant="secondary">{role}</Badge>;
    }
  };

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
      case "banned":
        return <Badge className="bg-destructive text-destructive-foreground">Banned</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <Star
          key={i}
          className={`w-4 h-4 ${i <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
        />
      );
    }
    return stars;
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold">Customer Management</h1>
            <p className="text-muted-foreground mt-2">
              Manage your customers and view their information
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              Filter & Sort
            </Button>
            {/* Debug button to test dialog */}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => {
                console.log("Debug: Testing dialog with first customer");
                if (customers.length > 0) {
                  handleViewProfile(customers[0]);
                }
              }}
            >
              Test View Profile
            </Button>
          </div>
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

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search customers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
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
                          {getRoleBadge(customer.role)}
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
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => handleViewProfile(customer)}>
                    <Eye className="w-4 h-4 mr-1" />
                    View Profile
                  </Button>
                  <Button 
                    variant="default" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => handleEditCustomer(customer)}
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button 
                    variant={customer.isBanned ? "default" : "destructive"} 
                    size="sm" 
                    className="flex-1"
                    onClick={() => handleBanCustomer(customer)}
                  >
                    {customer.isBanned ? (
                      <>
                        <UserCheck className="w-4 h-4 mr-1" />
                        Unban
                      </>
                    ) : (
                      <>
                        <Ban className="w-4 h-4 mr-1" />
                        Ban
                      </>
                    )}
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

        {/* Edit Customer Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Edit Customer</DialogTitle>
              <DialogDescription>
                Modify customer information and role
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit-name">Name</Label>
                <Input
                  id="edit-name"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  placeholder="Enter customer name"
                />
              </div>
              <div>
                <Label htmlFor="edit-email">Email</Label>
                <Input
                  id="edit-email"
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  placeholder="Enter customer email"
                />
              </div>
              <div>
                <Label htmlFor="edit-phone">Phone</Label>
                <Input
                  id="edit-phone"
                  value={editForm.phone}
                  onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                  placeholder="Enter customer phone"
                />
              </div>
              <div>
                <Label htmlFor="edit-role">Role</Label>
                <Select value={editForm.role} onValueChange={(value) => setEditForm({ ...editForm, role: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">User</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="delivery">Delivery Partner</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2 pt-4">
                <Button onClick={handleSaveEdit} className="flex-1">Save Changes</Button>
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>Cancel</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* View Profile Dialog */}
        <Dialog open={isViewProfileDialogOpen} onOpenChange={(open) => {
          console.log("Dialog open state changed to:", open);
          setIsViewProfileDialogOpen(open);
        }}>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Customer Profile</DialogTitle>
              <DialogDescription>
                Detailed information about the customer
              </DialogDescription>
            </DialogHeader>
            {selectedCustomer ? (
              <div className="space-y-6">
                {/* Header Section */}
                <div className="text-center border-b pb-4">
                  <div className="w-20 h-20 gradient-primary rounded-full flex items-center justify-center mx-auto mb-3">
                    <Users className="w-10 h-10 text-primary-foreground" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground mb-2">
                    {selectedCustomer.name}
                  </h3>
                  <div className="flex items-center justify-center gap-2 mb-3">
                    {getRoleBadge(selectedCustomer.role)}
                    {getTierBadge(selectedCustomer.tier)}
                    {getStatusBadge(selectedCustomer.status)}
                  </div>
                  <div className="flex items-center justify-center">
                    {renderStars(selectedCustomer.rating)}
                    <span className="ml-2 text-sm text-muted-foreground">
                      {selectedCustomer.rating} Rating
                    </span>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-foreground border-b pb-2">Contact Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="flex items-center text-sm">
                      <Mail className="w-4 h-4 mr-2 text-muted-foreground" />
                      <span className="font-medium">Email:</span>
                      <span className="ml-2 text-muted-foreground">{selectedCustomer.email}</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Phone className="w-4 h-4 mr-2 text-muted-foreground" />
                      <span className="font-medium">Phone:</span>
                      <span className="ml-2 text-muted-foreground">{selectedCustomer.phone}</span>
                    </div>
                    <div className="flex items-start text-sm md:col-span-2">
                      <MapPin className="w-4 h-4 mr-2 text-muted-foreground mt-0.5" />
                      <span className="font-medium">Address:</span>
                      <span className="ml-2 text-muted-foreground">{selectedCustomer.address}</span>
                    </div>
                  </div>
                </div>

                {/* Account Details */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-foreground border-b pb-2">Account Details</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="text-sm">
                      <span className="font-medium">Join Date:</span>
                      <span className="ml-2 text-muted-foreground">{selectedCustomer.joinDate}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Last Booking:</span>
                      <span className="ml-2 text-muted-foreground">{selectedCustomer.lastBooking}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Customer ID:</span>
                      <span className="ml-2 text-muted-foreground">#{selectedCustomer.id}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Status:</span>
                      <span className="ml-2">{getStatusBadge(selectedCustomer.status)}</span>
                    </div>
                  </div>
                </div>

                {/* Statistics */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-foreground border-b pb-2">Statistics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <p className="text-2xl font-bold text-foreground">{selectedCustomer.totalBookings}</p>
                      <p className="text-xs text-muted-foreground">Total Bookings</p>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <p className="text-2xl font-bold text-foreground">${selectedCustomer.totalSpent.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">Total Spent</p>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <p className="text-2xl font-bold text-foreground">{selectedCustomer.activeRentals}</p>
                      <p className="text-xs text-muted-foreground">Active Rentals</p>
                    </div>
                    <div className="text-center p-3 bg-muted rounded-lg">
                      <p className="text-2xl font-bold text-foreground">{selectedCustomer.rating}</p>
                      <p className="text-xs text-muted-foreground">Rating</p>
                    </div>
                  </div>
                </div>

                {/* Notes */}
                {selectedCustomer.notes && (
                  <div className="space-y-3">
                    <h4 className="font-semibold text-foreground border-b pb-2">Notes</h4>
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">{selectedCustomer.notes}</p>
                    </div>
                  </div>
                )}

                {/* Active Rentals Alert */}
                {selectedCustomer.activeRentals > 0 && (
                  <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                    <div className="flex items-center text-primary">
                      <Package className="w-4 h-4 mr-2" />
                      <span className="text-sm font-medium">
                        {selectedCustomer.activeRentals} Active Rental{selectedCustomer.activeRentals > 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-12 text-center">
                <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No customer selected</h3>
                <p className="text-muted-foreground mb-4">
                  Please click on a customer to view their profile.
                </p>
              </div>
            )}
            <div className="flex gap-2 pt-4 border-t">
              <Button 
                variant="outline" 
                onClick={() => {
                  setIsViewProfileDialogOpen(false);
                  handleEditCustomer(selectedCustomer);
                }}
                disabled={!selectedCustomer}
              >
                Edit Customer
              </Button>
              <Button 
                variant={selectedCustomer?.isBanned ? "default" : "destructive"} 
                onClick={() => {
                  setIsViewProfileDialogOpen(false);
                  handleBanCustomer(selectedCustomer);
                }}
                className="ml-auto"
                disabled={!selectedCustomer}
              >
                {selectedCustomer?.isBanned ? (
                  <>
                    <UserCheck className="w-4 h-4 mr-2" />
                    Unban Customer
                  </>
                ) : (
                  <>
                    <Ban className="w-4 h-4 mr-2" />
                    Ban Customer
                  </>
                )}
              </Button>
              <Button onClick={() => setIsViewProfileDialogOpen(false)}>Close</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default Customers;