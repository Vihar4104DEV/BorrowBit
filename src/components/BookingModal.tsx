import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { DateRangePicker } from './ui/date-range-picker';
import { TimePicker } from './ui/time-picker';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { 
  Calendar,
  Clock,
  CreditCard,
  DollarSign,
  Package,
  CheckCircle,
  Loader2,
  Shield,
  Truck,
  User,
  Mail,
  Phone,
  MapPin
} from 'lucide-react';
import { DateRange } from 'react-day-picker';
import { toast } from 'sonner';
import PaymentSuccess from './PaymentSuccess';

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  product: any;
}

const BookingModal: React.FC<BookingModalProps> = ({ isOpen, onClose, product }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [showPaymentSuccess, setShowPaymentSuccess] = useState(false);
  const [bookingData, setBookingData] = useState({
    dateRange: undefined as DateRange | undefined,
    pickupTime: '',
    returnTime: '',
    quantity: 1,
    customerInfo: {
      name: '',
      email: '',
      phone: '',
      address: ''
    },
    paymentMethod: 'card',
    cardNumber: '',
    expiryDate: '',
    cvv: ''
  });

  const calculateTotal = () => {
    if (!bookingData.dateRange?.from || !bookingData.dateRange?.to) return { rentalCost: 0, deposit: 0, total: 0 };
    const days = Math.ceil(
      (bookingData.dateRange.to.getTime() - bookingData.dateRange.from.getTime()) / (1000 * 60 * 60 * 24)
    );
    const dailyRate = parseFloat(product?.basic_pricing?.daily_rate || '0');
    const deposit = parseFloat(product?.deposit_amount || '0');
    return {
      rentalCost: dailyRate * days * bookingData.quantity,
      deposit: deposit * bookingData.quantity,
      total: (dailyRate * days * bookingData.quantity) + (deposit * bookingData.quantity)
    };
  };

  const handleNext = () => {
    if (step === 1 && (!bookingData.dateRange?.from || !bookingData.dateRange?.to)) {
      toast.error('Please select rental dates');
      return;
    }
    if (step === 2 && (!bookingData.customerInfo.name || !bookingData.customerInfo.email)) {
      toast.error('Please fill in customer information');
      return;
    }
    setStep(step + 1);
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setLoading(false);
    setShowPaymentSuccess(true);
  };

  const handleSuccessClose = () => {
    setShowPaymentSuccess(false);
    setStep(1);
    onClose();
  };

  const total = calculateTotal();

  // Only show booking modal if not showing payment success
  return (
    <>
      <Dialog open={isOpen && !showPaymentSuccess} onOpenChange={onClose}>
        <DialogContent className="max-w-lg w-full max-h-[90vh] overflow-y-auto mx-2 rounded-xl shadow-lg bg-white p-0 sm:p-4">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-lg sm:text-xl font-bold">
              <Package className="w-5 h-5" />
              Book {product?.name}
            </DialogTitle>
            <DialogDescription className="text-sm sm:text-base">
              Complete your rental booking in a few simple steps
            </DialogDescription>
          </DialogHeader>

          {/* Progress Steps */}
          <div className="flex items-center justify-between mb-6 px-2 sm:px-4">
            {[1, 2, 3].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${
                  step >= stepNumber 
                    ? 'bg-primary text-white shadow-md' 
                    : 'bg-muted text-muted-foreground'
                }`}>
                  {stepNumber}
                </div>
                {stepNumber < 3 && (
                  <div className={`w-12 h-0.5 mx-2 ${
                    step > stepNumber ? 'bg-primary' : 'bg-muted'
                  }`} />
                )}
              </div>
            ))}
          </div>

          {/* Step 1: Rental Details */}
          {step === 1 && (
            <div className="space-y-6">
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <Calendar className="w-5 h-5" />
                    Rental Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Rental Period</Label>
                    <DateRangePicker
                      dateRange={bookingData.dateRange}
                      onDateRangeChange={(range) => setBookingData(prev => ({ ...prev, dateRange: range }))}
                      placeholder="Select rental dates"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Pickup Time</Label>
                      <TimePicker
                        time={bookingData.pickupTime}
                        onTimeChange={(time) => setBookingData(prev => ({ ...prev, pickupTime: time }))}
                        placeholder="Select pickup time"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Return Time</Label>
                      <TimePicker
                        time={bookingData.returnTime}
                        onTimeChange={(time) => setBookingData(prev => ({ ...prev, returnTime: time }))}
                        placeholder="Select return time"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Quantity</Label>
                    <Select 
                      value={bookingData.quantity.toString()} 
                      onValueChange={(value) => setBookingData(prev => ({ ...prev, quantity: parseInt(value) }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: product?.available_quantity || 1 }, (_, i) => i + 1).map(num => (
                          <SelectItem key={num} value={num.toString()}>
                            {num} {num === 1 ? 'unit' : 'units'}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
              {total.total > 0 && (
                <Card className="bg-green-50 border-green-200 rounded-lg shadow-sm">
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Rental Cost:</span>
                        <span className="font-medium">${total.rentalCost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Deposit:</span>
                        <span className="font-medium">${total.deposit.toFixed(2)}</span>
                      </div>
                      <div className="border-t pt-2 flex justify-between font-semibold">
                        <span>Total:</span>
                        <span className="text-green-600">${total.total.toFixed(2)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Step 2: Customer Information */}
          {step === 2 && (
            <div className="space-y-6">
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <User className="w-5 h-5" />
                    Customer Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name *</Label>
                      <Input
                        id="name"
                        value={bookingData.customerInfo.name}
                        onChange={(e) => setBookingData(prev => ({
                          ...prev,
                          customerInfo: { ...prev.customerInfo, name: e.target.value }
                        }))}
                        placeholder="Enter your full name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={bookingData.customerInfo.email}
                        onChange={(e) => setBookingData(prev => ({
                          ...prev,
                          customerInfo: { ...prev.customerInfo, email: e.target.value }
                        }))}
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        value={bookingData.customerInfo.phone}
                        onChange={(e) => setBookingData(prev => ({
                          ...prev,
                          customerInfo: { ...prev.customerInfo, phone: e.target.value }
                        }))}
                        placeholder="Enter your phone number"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="address">Delivery Address</Label>
                      <Input
                        id="address"
                        value={bookingData.customerInfo.address}
                        onChange={(e) => setBookingData(prev => ({
                          ...prev,
                          customerInfo: { ...prev.customerInfo, address: e.target.value }
                        }))}
                        placeholder="Enter delivery address"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Step 3: Payment */}
          {step === 3 && (
            <div className="space-y-6">
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <CreditCard className="w-5 h-5" />
                    Payment Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Payment Method</Label>
                    <Select 
                      value={bookingData.paymentMethod} 
                      onValueChange={(value) => setBookingData(prev => ({ ...prev, paymentMethod: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="card">Credit/Debit Card</SelectItem>
                        <SelectItem value="paypal">Stripe</SelectItem>
                        <SelectItem value="bank">Bank Transfer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {bookingData.paymentMethod === 'card' && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="cardNumber">Card Number</Label>
                        <Input
                          id="cardNumber"
                          value={bookingData.cardNumber}
                          onChange={(e) => setBookingData(prev => ({ ...prev, cardNumber: e.target.value }))}
                          placeholder="1234 5678 9012 3456"
                          maxLength={19}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="expiry">Expiry Date</Label>
                          <Input
                            id="expiry"
                            value={bookingData.expiryDate}
                            onChange={(e) => setBookingData(prev => ({ ...prev, expiryDate: e.target.value }))}
                            placeholder="MM/YY"
                            maxLength={5}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="cvv">CVV</Label>
                          <Input
                            id="cvv"
                            value={bookingData.cvv}
                            onChange={(e) => setBookingData(prev => ({ ...prev, cvv: e.target.value }))}
                            placeholder="123"
                            maxLength={4}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                  <Card className="bg-blue-50 border-blue-200 rounded-lg shadow-sm">
                    <CardContent className="p-4">
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Rental Cost:</span>
                          <span className="font-medium">${total.rentalCost.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Deposit:</span>
                          <span className="font-medium">${total.deposit.toFixed(2)}</span>
                        </div>
                        <div className="border-t pt-2 flex justify-between font-semibold text-lg">
                          <span>Total Amount:</span>
                          <span className="text-blue-600">${total.total.toFixed(2)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </CardContent>
              </Card>
            </div>
          )}

          <DialogFooter className="flex flex-col sm:flex-row justify-between gap-2 mt-4">
            <div className="flex gap-2">
              {step > 1 && (
                <Button variant="outline" onClick={handleBack}>
                  Back
                </Button>
              )}
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
            </div>
            <div className="flex gap-2">
              {step < 3 ? (
                <Button onClick={handleNext}>
                  Next Step
                </Button>
              ) : (
                <Button onClick={handleSubmit} disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing Payment...
                    </>
                  ) : (
                    <>
                      <CreditCard className="w-4 h-4 mr-2" />
                      Confirm Booking
                    </>
                  )}
                </Button>
              )}
            </div>
          </DialogFooter>

          {/* Loader Overlay */}
          {loading && (
            <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 rounded-xl">
              <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
                <Loader2 className="w-8 h-8 mb-2 animate-spin text-primary" />
                <span className="font-medium text-primary">Processing Payment...</span>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Payment Success Modal */}
      <PaymentSuccess
        isVisible={showPaymentSuccess}
        onClose={handleSuccessClose}
        bookingData={bookingData}
        product={product}
      />
    </>
  );
};

export default BookingModal;
