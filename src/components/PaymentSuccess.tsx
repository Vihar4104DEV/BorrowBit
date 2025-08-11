import React, { useEffect, useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { 
  CheckCircle, 
  CreditCard, 
  Calendar, 
  Package,
  Download,
  Share2,
  Home,
  ArrowRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface PaymentSuccessProps {
  isVisible: boolean;
  onClose: () => void;
  bookingData?: any;
  product?: any;
}

const PaymentSuccess: React.FC<PaymentSuccessProps> = ({
  isVisible,
  onClose,
  bookingData,
  product
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (isVisible) {
      // Animate through steps
      const timer1 = setTimeout(() => setCurrentStep(1), 500);
      const timer2 = setTimeout(() => setCurrentStep(2), 1500);
      const timer3 = setTimeout(() => setCurrentStep(3), 2500);
      const timer4 = setTimeout(() => setShowDetails(true), 3500);

      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        clearTimeout(timer4);
      };
    }
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="w-full max-w-md"
        >
          <Card className="relative overflow-hidden">
            {/* Success Animation */}
            <div className="relative h-64 bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center">
              {/* Animated circles */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: currentStep >= 1 ? 1 : 0 }}
                transition={{ type: "spring", damping: 15, stiffness: 200 }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <div className="w-32 h-32 bg-white/20 rounded-full flex items-center justify-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: currentStep >= 2 ? 1 : 0 }}
                    transition={{ delay: 0.2, type: "spring", damping: 15, stiffness: 200 }}
                    className="w-24 h-24 bg-white/30 rounded-full flex items-center justify-center"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: currentStep >= 3 ? 1 : 0 }}
                      transition={{ delay: 0.4, type: "spring", damping: 15, stiffness: 200 }}
                      className="w-16 h-16 bg-white rounded-full flex items-center justify-center"
                    >
                      <CheckCircle className="w-8 h-8 text-green-600" />
                    </motion.div>
                  </motion.div>
                </div>
              </motion.div>

              {/* Success text */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: currentStep >= 3 ? 1 : 0, y: currentStep >= 3 ? 0 : 20 }}
                transition={{ delay: 0.6 }}
                className="absolute bottom-8 left-0 right-0 text-center text-white"
              >
                <h2 className="text-2xl font-bold mb-2">Payment Successful!</h2>
                <p className="text-white/90">Your booking has been confirmed</p>
              </motion.div>
            </div>

            <CardContent className="p-6">
              {/* Booking Details */}
              <AnimatePresence>
                {showDetails && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-4"
                  >
                    {/* Product Info */}
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Package className="w-6 h-6 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-sm truncate">
                          {product?.name || 'Product Name'}
                        </h3>
                        <p className="text-xs text-muted-foreground">
                          Booking ID: #{Math.random().toString(36).substr(2, 9).toUpperCase()}
                        </p>
                      </div>
                    </div>

                    {/* Booking Summary */}
                    <div className="space-y-3">
                      <h4 className="font-semibold text-sm">Booking Summary</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Rental Period:</span>
                          <span className="font-medium">
                            {bookingData?.dateRange?.from ? 
                              `${new Date(bookingData.dateRange.from).toLocaleDateString()} - ${new Date(bookingData.dateRange.to).toLocaleDateString()}` : 
                              'Not specified'
                            }
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Quantity:</span>
                          <span className="font-medium">{bookingData?.quantity || 1}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Total Amount:</span>
                          <span className="font-semibold text-green-600">
                            ${bookingData?.total || '0.00'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="grid grid-cols-2 gap-3 pt-4">
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Download className="w-4 h-4" />
                        Download Receipt
                      </Button>
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Share2 className="w-4 h-4" />
                        Share
                      </Button>
                    </div>

                    {/* Continue Button */}
                    <Button 
                      onClick={onClose} 
                      className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
                    >
                      <Home className="w-4 h-4 mr-2" />
                      Continue Shopping
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PaymentSuccess;
