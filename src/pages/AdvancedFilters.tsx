import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const AdvancedFilters = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-3xl mx-auto py-8 px-4">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle>Advanced Booking Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4">
              <input className="w-full p-2 border rounded" placeholder="Customer Name" />
              <input className="w-full p-2 border rounded" placeholder="Product Name" />
              <input className="w-full p-2 border rounded" placeholder="Booking ID" />
              <input className="w-full p-2 border rounded" type="date" placeholder="Start Date" />
              <input className="w-full p-2 border rounded" type="date" placeholder="End Date" />
              <Button variant="hero" size="lg" type="submit">Apply Filters</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdvancedFilters;
