import { useParams, useNavigate } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, User, Package, DollarSign, Edit, FileText, Send } from "lucide-react";

const sampleBooking = {
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
};

const getStatusBadge = (status) => {
  switch (status) {
    case "confirmed":
      return <Badge className="bg-success text-success-foreground">Confirmed</Badge>;
    case "pending":
      return <Badge className="bg-warning text-warning-foreground">Pending</Badge>;
    case "active":
      return <Badge className="bg-primary text-primary-foreground">Active</Badge>;
    case "overdue":
      return <Badge variant="destructive">Overdue</Badge>;
    case "completed":
      return <Badge className="bg-muted text-muted-foreground">Completed</Badge>;
    case "cancelled":
      return <Badge variant="destructive">Cancelled</Badge>;
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
};

const BookingDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  // In real app, fetch booking by id
  const booking = sampleBooking;
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto py-8 px-4">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Booking Details</CardTitle>
            <div className="flex items-center gap-2 mt-2">
              {getStatusBadge(booking.status)}
              <span className="text-lg font-semibold">ID: {booking.id}</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-semibold mb-2 flex items-center"><User className="w-4 h-4 mr-1" />Customer</h4>
                <p className="text-muted-foreground">{booking.customer}</p>
                <p className="text-muted-foreground">{booking.email}</p>
                <p className="text-muted-foreground">{booking.phone}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center"><Package className="w-4 h-4 mr-1" />Product</h4>
                <p className="text-muted-foreground">{booking.product}</p>
                <p className="text-muted-foreground">Category: {booking.category}</p>
                <p className="text-muted-foreground">Deposit: ${booking.deposit}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center"><Calendar className="w-4 h-4 mr-1" />Rental Period</h4>
                <p className="text-muted-foreground">Start: {booking.startDate}</p>
                <p className="text-muted-foreground">End: {booking.endDate}</p>
                <p className="text-muted-foreground">Duration: {booking.duration}</p>
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center"><DollarSign className="w-4 h-4 mr-1" />Financial</h4>
                <p className="text-muted-foreground">Total: ${booking.amount}</p>
                <p className="text-muted-foreground">Created: {booking.createdDate}</p>
              </div>
            </div>
            {booking.notes && (
              <div className="p-3 bg-muted rounded-lg mb-4">
                <strong>Notes:</strong> {booking.notes}
              </div>
            )}
            <div className="flex flex-wrap gap-2 mt-4">
              <Button variant="default" onClick={() => navigate(`/bookings/edit/${booking.id}`)}>
                <Edit className="w-4 h-4 mr-1" />Edit Booking
              </Button>
              <Button variant="success" onClick={() => navigate(`/bookings/contract/${booking.id}`)}>
                <FileText className="w-4 h-4 mr-1" />Generate Contract
              </Button>
              <Button variant="hero" onClick={() => navigate(`/bookings/notify/${booking.id}`)}>
                <Send className="w-4 h-4 mr-1" />Send Notification
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BookingDetail;
