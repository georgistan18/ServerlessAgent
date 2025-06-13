import { Inngest } from "inngest";

// Initialize the Inngest client for our app
export const inngest = new Inngest({ 
  id: "ai-newsletter",
  eventKey: process.env.INNGEST_EVENT_KEY 
}); 
