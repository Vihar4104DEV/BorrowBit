import { useParams } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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

const GenerateContract = () => {
  const { id } = useParams();
  // In real app, fetch booking by id
  const booking = sampleBooking;
  const contractText = `
RENTAL CONTRACT

Booking ID: ${booking.id}
Customer: ${booking.customer}
Product: ${booking.product}
Rental Period: ${booking.startDate} to ${booking.endDate}
Deposit: $${booking.deposit}
Total Amount: $${booking.amount}

Terms & Conditions:
- The product must be returned in original condition.
- Late returns will incur additional charges.
- Deposit will be refunded after inspection.
`;
  const handleDownload = () => {
    // Simulate PDF download
    alert("Contract PDF downloaded!");
  };
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto py-8 px-4">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Rental Contract</CardTitle>
            <span className="text-lg font-semibold mt-2">Booking ID: {booking.id}</span>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted p-4 rounded mb-4 whitespace-pre-wrap text-sm">{contractText}</pre>
            <Button variant="hero" size="lg" onClick={handleDownload}>Download Contract PDF</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default GenerateContract;
