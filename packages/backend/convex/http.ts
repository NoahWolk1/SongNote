import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

const aiBackendUrl = "https://rocketlaunchers-ai-singer.hf.space/generate-singing";

http.route({
  path: "/api/generate-singing",
  method: "POST",
  handler: httpAction(async (ctx, req) => {
    try {
      const body = await req.json();
      console.log("Forwarding request to AI backend:", body);
      
      // Forward the request to your Hugging Face Space
      const aiResponse = await fetch(aiBackendUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      
      if (!aiResponse.ok) {
        console.error("AI backend error:", aiResponse.status, aiResponse.statusText);
        return new Response(JSON.stringify({ error: "AI backend error" }), {
          status: aiResponse.status,
          headers: { "Content-Type": "application/json" },
        });
      }
      
      const aiData = await aiResponse.json();
      console.log("AI backend response:", aiData);
      
      return new Response(JSON.stringify(aiData), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (error) {
      console.error("HTTP route error:", error);
      return new Response(JSON.stringify({ error: "Internal server error" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  }),
});

export default http; 