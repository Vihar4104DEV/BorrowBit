import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Calendar, User, Package, DollarSign } from "lucide-react";

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

const EditBooking = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  // In real app, fetch booking by id
  const booking = sampleBooking;
  const [form, setForm] = useState({
    customer: booking.customer,
    email: booking.email,
    phone: booking.phone,
    product: booking.product,
    category: booking.category,
    startDate: booking.startDate,
    endDate: booking.endDate,
    amount: booking.amount,
    deposit: booking.deposit,
    notes: booking.notes
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Save logic here
    alert("Booking updated successfully!");
    navigate(`/bookings/${booking.id}`);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto py-8 px-4">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Edit Booking</CardTitle>
            <span className="text-lg font-semibold mt-2">ID: {booking.id}</span>
          </CardHeader>
          <CardContent>
            <form className="grid grid-cols-1 md:grid-cols-2 gap-6" onSubmit={handleSubmit}>
              <div>
                <label className="font-semibold mb-1 block">Customer</label>
                <Input name="customer" value={form.customer} onChange={handleChange} required />
                <label className="font-semibold mb-1 block mt-4">Email</label>
                <Input name="email" value={form.email} onChange={handleChange} required type="email" />
                <label className="font-semibold mb-1 block mt-4">Phone</label>
                <Input name="phone" value={form.phone} onChange={handleChange} required />
              </div>
              <div>
                <label className="font-semibold mb-1 block">Product</label>
                <Input name="product" value={form.product} onChange={handleChange} required />
                <label className="font-semibold mb-1 block mt-4">Category</label>
                <Input name="category" value={form.category} onChange={handleChange} required />
                <label className="font-semibold mb-1 block mt-4">Deposit</label>
                <Input name="deposit" value={form.deposit} onChange={handleChange} required type="number" />
              </div>
              <div>
                <label className="font-semibold mb-1 block">Start Date</label>
                <Input name="startDate" value={form.startDate} onChange={handleChange} required type="date" />
                <label className="font-semibold mb-1 block mt-4">End Date</label>
                <Input name="endDate" value={form.endDate} onChange={handleChange} required type="date" />
              </div>
              <div>
                <label className="font-semibold mb-1 block">Amount</label>
                <Input name="amount" value={form.amount} onChange={handleChange} required type="number" />
                <label className="font-semibold mb-1 block mt-4">Notes</label>
                <Input name="notes" value={form.notes} onChange={handleChange} />
              </div>
              <div className="col-span-2 flex gap-2 mt-6">
                <Button variant="hero" type="submit">Save Changes</Button>
                <Button variant="outline" type="button" onClick={() => navigate(`/bookings/${booking.id}`)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EditBooking;
