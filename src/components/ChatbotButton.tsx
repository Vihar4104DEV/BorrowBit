import { useEffect, useState } from "react";
import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Add this at the top (after imports) to extend the Window interface
declare global {
  interface Window {
    chatbase?: any;
  }
}

export const ChatbotButton = () => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const openHandler = () => setOpen(true);
    const closeHandler = () => setOpen(false);
    const toggleHandler = () => setOpen((v) => !v);
    window.addEventListener("chatbot:open", openHandler as EventListener);
    window.addEventListener("chatbot:close", closeHandler as EventListener);
    window.addEventListener("chatbot:toggle", toggleHandler as EventListener);
    return () => {
      window.removeEventListener("chatbot:open", openHandler as EventListener);
      window.removeEventListener("chatbot:close", closeHandler as EventListener);
      window.removeEventListener("chatbot:toggle", toggleHandler as EventListener);
    };
  }, []);

  // Inject Chatbase script
  useEffect(() => {
    (function () {
      if (!window.chatbase || window.chatbase("getState") !== "initialized") {
        window.chatbase = (...args: any[]) => {
          if (!window.chatbase.q) {
            window.chatbase.q = [];
          }
          window.chatbase.q.push(args);
        };
        window.chatbase = new Proxy(window.chatbase, {
          get(target, prop) {
            if (prop === "q") {
              return target.q;
            }
            return (...args: any[]) => target(prop, ...args);
          },
        });
      }
      const onLoad = function () {
        const script = document.createElement("script");
        script.src = "https://www.chatbase.co/embed.min.js";
        script.id = "4xcpVZfKDjAMm8iZeNO0W";
        // script.domain = "www.chatbase.co"; // Removed, not valid
        document.body.appendChild(script);
      };
      if (document.readyState === "complete") {
        onLoad();
      } else {
        window.addEventListener("load", onLoad);
      }
    })();
  }, []);

  return (
    <>
      {/* Chatbase script logic moved to useEffect above */}
      <div className="fixed bottom-5 right-5 z-50">
        <Button
          variant="hero"
          size="icon"
          className="rounded-full w-12 h-12 shadow-elegant"
          onClick={() => setOpen((v) => !v)}
          aria-label="Open Chatbot"
        >
          <MessageCircle className="w-5 h-5" />
        </Button>
      </div>

      {open && (
        <div className="fixed bottom-20 right-5 z-50 w-[340px] max-w-[90vw]">
          <Card className="shadow-elegant">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Assistant</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                This is a placeholder for your chatbot widget/integration.
              </div>
              <div className="mt-3 text-xs text-muted-foreground">
                Add your chat provider or custom logic here.
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};


