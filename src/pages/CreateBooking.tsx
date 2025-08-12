import { Navigation } from "@/components/Navigation";

const CreateBooking = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-3xl mx-auto py-8 px-4">
        <h1 className="text-2xl font-bold mb-4">Create New Booking</h1>
        <p>Booking creation form will be shown here.</p>
      </div>
    </div>
  );
};

export default CreateBooking;
