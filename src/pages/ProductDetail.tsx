import { useMemo, useState } from "react";
import { useParams, Link, useNavigate, useLocation } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Calendar as CalendarIcon, Heart, Minus, Plus, Package, ShoppingCart } from "lucide-react";
import { products, getProductById } from "@/data/products";
import { useCart } from "@/contexts/CartContext";
import { useToast } from "@/hooks/use-toast";
import { DateSelectionDialog } from "@/components/DateSelectionDialog";

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { addToCart } = useCart();
  const productId = Number(id);
  const product = useMemo(() => getProductById(productId), [productId]);

  // Determine where to go back based on referrer
  const getBackPath = () => {
    const referrer = location.state?.from || document.referrer;
    if (referrer.includes('/my-products')) {
      return '/my-products';
    }
    return '/products';
  };

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [qty, setQty] = useState(1);
  const [coupon, setCoupon] = useState("");
  const [isDateDialogOpen, setIsDateDialogOpen] = useState(false);

  const handleAddToCartClick = () => {
    setIsDateDialogOpen(true);
  };

  const handleDateSelectionConfirm = (fromDate: string, toDate: string, quantity: number) => {
    addToCart(productId, quantity, fromDate, toDate, product.dailyRate);
    toast({
      title: "Added to Cart",
      description: `${quantity} ${quantity === 1 ? 'item' : 'items'} of ${product.name} added to cart successfully!`,
    });
  };

  if (!product) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="text-muted-foreground">Product not found.</div>
          <Button variant="link" onClick={() => navigate(-1)}>Go back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="text-sm text-muted-foreground mb-6">
          <Link to={getBackPath()} className="underline">All Products</Link> / <span className="text-foreground">{product.name}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Left: Image and wishlist */}
          <div>
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="w-full aspect-square rounded-xl bg-muted flex items-center justify-center">
                  {product.image ? (
                    <img src={product.image} alt={product.name} className="w-full h-full object-cover rounded-xl" />
                  ) : (
                    <Package className="w-16 h-16 text-muted-foreground" />
                  )}
                </div>
                <div className="mt-6 flex justify-center">
                  <Button variant="outline" className="rounded-full px-8" size="lg">
                    <Heart className="w-4 h-4 mr-2" />
                    Add to wish list
                  </Button>
                </div>

                <div className="mt-8">
                  <div className="text-sm text-muted-foreground mb-2">Product descriptions</div>
                  <p className="text-foreground leading-relaxed">{product.description}</p>
                  <Button variant="link" className="px-0 mt-2">Read More &gt;</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right: Details and booking */}
          <div>
            <div className="mb-4 flex items-center justify-between">
              <h1 className="text-3xl font-bold text-foreground">{product.name}</h1>
              <Button variant="outline">Price List</Button>
            </div>

            <div className="text-xl text-foreground font-semibold mb-6">
              ₹ {product.weeklyRate} <span className="text-sm text-muted-foreground">( ₹{product.dailyRate} / per unit )</span>
            </div>

                         {/* Date range */}
             <div className="flex items-center gap-3 mb-6">
               <span className="text-lg font-semibold text-foreground">From:</span>
               <div className="flex items-center gap-2">
                 <Input 
                   type="date" 
                   value={fromDate} 
                   onChange={(e) => setFromDate(e.target.value)} 
                   className="w-36" 
                 />
                 <CalendarIcon className="w-5 h-5 text-muted-foreground" />
               </div>
               <span className="text-lg font-semibold text-foreground">to</span>
               <div className="flex items-center gap-2">
                 <Input 
                   type="date" 
                   value={toDate} 
                   onChange={(e) => setToDate(e.target.value)} 
                   className="w-36" 
                 />
                 <CalendarIcon className="w-5 h-5 text-muted-foreground" />
               </div>
               <Badge variant="secondary">Ultimate Yak</Badge>
             </div>

            {/* Quantity and Add to Cart */}
            <div className="flex items-center gap-4 mb-8">
              <div className="flex items-center rounded-lg border bg-muted">
                <Button type="button" variant="ghost" className="px-3" onClick={() => setQty((q) => Math.max(1, q - 1))}>
                  <Minus className="w-4 h-4" />
                </Button>
                <div className="px-6 py-2 text-foreground font-medium">{qty}</div>
                <Button type="button" variant="ghost" className="px-3" onClick={() => setQty((q) => q + 1)}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
                             <Button variant="outline" size="lg" className="px-6" onClick={handleAddToCartClick}>
                 <ShoppingCart className="w-4 h-4 mr-2" /> Add to Cart
               </Button>
            </div>

            {/* Coupon */}
            <div className="mb-10">
              <div className="mb-2 font-semibold text-foreground">Apply Coupon</div>
              <div className="flex gap-2">
                <Input placeholder="Coupon Code" value={coupon} onChange={(e) => setCoupon(e.target.value)} />
                <Button variant="default">Apply</Button>
              </div>
            </div>

            {/* Terms and share */}
            <div className="space-y-4">
              <div>
                <div className="font-semibold text-foreground">Terms & condition</div>
                <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1 mt-2">
                  <li>All rentals are subject to availability.</li>
                  <li>Security deposit may be required.</li>
                  <li>Late returns will incur additional charges.</li>
                </ul>
              </div>
              <div>
                <div className="font-semibold text-foreground">Share :</div>
                <div className="text-sm text-muted-foreground">[social buttons placeholder]</div>
              </div>
            </div>
                     </div>
         </div>
       </div>

       {/* Date Selection Dialog */}
       <DateSelectionDialog
         isOpen={isDateDialogOpen}
         onClose={() => setIsDateDialogOpen(false)}
         onConfirm={handleDateSelectionConfirm}
         productName={product.name}
         dailyRate={product.dailyRate}
       />
     </div>
   );
 };

export default ProductDetail;
