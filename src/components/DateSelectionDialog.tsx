import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Calendar, Minus, Plus } from "lucide-react";

interface DateSelectionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (fromDate: string, toDate: string, quantity: number) => void;
  productName: string;
  dailyRate: number;
}

export function DateSelectionDialog({
  isOpen,
  onClose,
  onConfirm,
  productName,
  dailyRate,
}: DateSelectionDialogProps) {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [quantity, setQuantity] = useState(1);

  const handleConfirm = () => {
    if (!fromDate || !toDate) {
      return;
    }
    onConfirm(fromDate, toDate, quantity);
    onClose();
    // Reset form
    setFromDate("");
    setToDate("");
    setQuantity(1);
  };

  const calculateDays = () => {
    if (!fromDate || !toDate) return 0;
    const from = new Date(fromDate);
    const to = new Date(toDate);
    const diffTime = Math.abs(to.getTime() - from.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays || 0;
  };

  const calculateTotal = () => {
    const days = calculateDays();
    return days * quantity * dailyRate;
  };

  const days = calculateDays();
  const total = calculateTotal();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Select Rental Dates</DialogTitle>
          <DialogDescription>
            Choose your rental period for <strong>{productName}</strong>
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Date Selection */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="from-date">From Date</Label>
                <div className="relative">
                  <Input
                    id="from-date"
                    type="date"
                    value={fromDate}
                    onChange={(e) => setFromDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="pr-10"
                  />
                  <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="to-date">To Date</Label>
                <div className="relative">
                  <Input
                    id="to-date"
                    type="date"
                    value={toDate}
                    onChange={(e) => setToDate(e.target.value)}
                    min={fromDate || new Date().toISOString().split('T')[0]}
                    className="pr-10"
                  />
                  <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                </div>
              </div>
            </div>
          </div>

          {/* Quantity Selection */}
          <div className="space-y-2">
            <Label>Quantity</Label>
            <div className="flex items-center gap-4">
              <div className="flex items-center rounded-lg border bg-muted">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="px-3"
                  onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                >
                  <Minus className="w-4 h-4" />
                </Button>
                <div className="px-6 py-2 text-foreground font-medium">{quantity}</div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="px-3"
                  onClick={() => setQuantity((q) => q + 1)}
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Summary */}
          {days > 0 && (
            <div className="bg-muted p-4 rounded-lg space-y-2">
              <div className="flex justify-between text-sm">
                <span>Rental Period:</span>
                <span className="font-medium">{days} {days === 1 ? 'day' : 'days'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Daily Rate:</span>
                <span className="font-medium">${dailyRate}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Quantity:</span>
                <span className="font-medium">{quantity}</span>
              </div>
              <div className="border-t pt-2 flex justify-between font-semibold">
                <span>Total:</span>
                <span>${total}</span>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleConfirm}
            disabled={!fromDate || !toDate || days <= 0}
          >
            Add to Cart
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
