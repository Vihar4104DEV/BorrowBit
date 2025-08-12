import { useParams } from "react-router-dom";
import { useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const SendNotification = () => {
  const { id } = useParams();
  const [type, setType] = useState("Email");
  const [message, setMessage] = useState("");
  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Notification sent via ${type}!`);
    setMessage("");
  };
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto py-8 px-4">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Send Notification</CardTitle>
            <span className="text-lg font-semibold mt-2">Booking ID: {id}</span>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <label className="font-semibold mb-1 block">Notification Type</label>
              <select className="w-full p-2 border rounded" value={type} onChange={e => setType(e.target.value)}>
                <option>Email</option>
                <option>SMS</option>
                <option>WhatsApp</option>
              </select>
              <label className="font-semibold mb-1 block mt-4">Message</label>
              <textarea className="w-full p-2 border rounded" rows={4} placeholder="Type your message here..." value={message} onChange={e => setMessage(e.target.value)} required />
              <Button variant="hero" size="lg" type="submit">Send Notification</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SendNotification;
