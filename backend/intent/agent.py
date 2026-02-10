import os
from backend.intent.graph import create_swarm
from langchain_core.messages import HumanMessage

# Forward declaration or import if needed, but for now just fixing os
from backend.pipeline import QyntaraPipeline


class QyntaraAgent:
    def __init__(self, pipeline: QyntaraPipeline):
        self.pipeline = pipeline
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found. Agent will not function.")
            self.graph = None
            return

        self.graph = create_swarm(pipeline)

    async def process_command(self, user_input: str) -> str:
        if not self.graph:
            return (
                "⚠️ **Neural Link Offline**\n\n"
                "The Neural Command Center requires an OpenAI API Key to function.\n"
                "Please set the `OPENAI_API_KEY` environment variable in your system or `.env` file.\n\n"
                "You can still use the manual controls in the other tabs."
            )
        
        try:
            # Run the graph
            # We initialize state with the user message
            initial_state = {"messages": [HumanMessage(content=user_input)], "next_step": "", "current_mesh": "backend/data/gen_model.obj"}
            
            final_response = ""
            async for output in self.graph.astream(initial_state):
                # We can stream intermediate steps here if we want
                for key, value in output.items():
                    if key != "Supervisor":
                        # It's an agent node output
                        last_msg = value["messages"][-1]
                        final_response += f"[{key}]: {last_msg.content}\n"
            
            return final_response if final_response else "Task Completed."
            
        except Exception as e:
            return f"Agent Error: {str(e)}"
