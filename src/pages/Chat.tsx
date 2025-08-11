import { useEffect } from "react";
import { Navigation } from "@/components/Navigation";

const Chat = () => {
  useEffect(() => {
    window.dispatchEvent(new Event("chatbot:open"));
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      {/* Rest of the page is empty; the floating chatbot opens automatically */}
    </div>
  );
};

export default Chat;


