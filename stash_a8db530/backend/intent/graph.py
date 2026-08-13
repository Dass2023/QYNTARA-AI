import operator
from typing import Annotated, List, Union, Sequence, TypedDict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, FunctionMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, END
from backend.intent.tools import QyntaraTools
from backend.pipeline import QyntaraPipeline

# Define the Agent State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    current_mesh: str

def create_swarm(pipeline: QyntaraPipeline):
    llm = ChatOpenAI(model="gpt-4-1106-preview")
    tools_wrapper = QyntaraTools(pipeline)
    tools = tools_wrapper.get_tools()
    
    # --- 1. Supervisor Agent ---
    # The supervisor decides which agent to call next based on the conversation.
    
    members = ["Generator", "Validator", "Remesher", "UVSpecialist", "MaterialSpecialist", "Exporter"]
    
    system_prompt = (
        "You are the Technical Director (TD) Supervisor of Qyntara AI. "
        "You manage a team of experts: \n"
        "1. Generator: Creates 3D assets.\n"
        "2. Validator: Checks geometry and topology.\n"
        "3. Remesher: Optimizes topology (Quad Remeshing).\n"
        "4. UVSpecialist: Unwraps meshes and generates UV layouts.\n"
        "5. MaterialSpecialist: Assigns materials and textures.\n"
        "6. Exporter: Handles final file export.\n"
        "Given the user's request, decide who should act next. "
        "If the task is finished, respond with 'FINISH'."
    )
    
    options = ["FINISH"] + members
    
    # Using structured output for routing
    class Route(BaseModel):
        next: str = Field(description="The next role to act.")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the conversation above, who should act next? Select one of: {options}"),
    ]).partial(options=str(options), members=", ".join(members))
    
    supervisor_chain = (
        prompt 
        | llm.with_structured_output(Route) 
        | (lambda x: {"next": x.next} if x else {"next": "FINISH"})
    )

    # --- 2. Node Definitions ---
    
    # Helper to create an agent node
    def create_agent_node(agent_name, tool_name):
        # Find the specific tool
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool: raise ValueError(f"Tool {tool_name} not found")
        
        async def agent_node(state):
            last_message = state["messages"][-1]
            current_mesh = state.get("current_mesh")
            
            # Construct system prompt with context
            context_str = f" Current active mesh: {current_mesh}" if current_mesh else " No active mesh."
            
            agent_prompt = ChatPromptTemplate.from_messages([
                ("system", f"You are the {agent_name}. You have access to the tool '{tool_name}'. "
                           f"Analyze the conversation and call your tool with the correct arguments.{context_str} "
                           "If the user implies the current mesh, use the path provided in context."),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            # Bind the specific tool to the LLM
            agent = agent_prompt | llm.bind_tools([tool])
            
            result = await agent.ainvoke(state)
            
            # If the agent decided to call a tool
            if result.tool_calls:
                tool_call = result.tool_calls[0]
                args = tool_call["args"]
                
                # Context Injection: If tool needs mesh_paths and it's missing/empty, inject current_mesh
                if "mesh_paths" in args and (not args["mesh_paths"] or args["mesh_paths"] == ["current_mesh"]):
                    if current_mesh:
                        args["mesh_paths"] = [current_mesh]
                
                # Execute tool
                tool_output_str = await tool.ainvoke(args)
                
                # Parse output to update state
                import json
                try:
                    output_data = json.loads(tool_output_str)
                    message_content = output_data.get("message", str(tool_output_str))
                    new_mesh = output_data.get("output_path")
                    
                    # Update state
                    state_update = {
                        "messages": [AIMessage(content=message_content, name=agent_name)]
                    }
                    if new_mesh:
                        state_update["current_mesh"] = new_mesh
                        
                    return state_update
                    
                except json.JSONDecodeError:
                    # Fallback for non-JSON output
                    return {"messages": [AIMessage(content=str(tool_output_str), name=agent_name)]}
            
            return {"messages": [result]}

        return agent_node

    # --- 3. Build Graph ---
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("Supervisor", lambda state: {"next_step": supervisor_chain.invoke(state)})
    
    # We map tools to agents
    # Generator -> generate_3d_from_text
    # Validator -> validate_mesh
    # Remesher -> extrude_floorplan (Wait, we need a remesh tool in tools.py first!)
    # Exporter -> export_mesh
    
    # Note: I need to update tools.py to include the remesher tool first!
    # For now, I'll use placeholders and update tools.py in the next step.
    
    workflow.add_node("Generator", create_agent_node("Generator", "generate_3d_from_text"))
    workflow.add_node("Validator", create_agent_node("Validator", "validate_mesh"))
    workflow.add_node("Exporter", create_agent_node("Exporter", "export_mesh"))
    workflow.add_node("Remesher", create_agent_node("Remesher", "remesh_model"))
    workflow.add_node("UVSpecialist", create_agent_node("UVSpecialist", "generate_uvs"))
    workflow.add_node("MaterialSpecialist", create_agent_node("MaterialSpecialist", "assign_material"))
    
    # Add Edges
    for member in ["Generator", "Validator", "Exporter", "Remesher", "UVSpecialist", "MaterialSpecialist"]:
        workflow.add_edge(member, "Supervisor")

    # Conditional Edges from Supervisor
    conditional_map = {k: k for k in ["Generator", "Validator", "Exporter", "Remesher", "UVSpecialist", "MaterialSpecialist"]}
    conditional_map["FINISH"] = END
    
    workflow.add_conditional_edges("Supervisor", lambda x: x["next_step"], conditional_map)
    
    workflow.set_entry_point("Supervisor")
    
    return workflow.compile()
