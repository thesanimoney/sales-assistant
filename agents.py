from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from uuid import uuid4

from schemas import CustomAgentState, Response, CustomContext
from tools import define_meeting_parameters, save_sales_analysis, save_technical_analysis
from middleware import dynamic_prompt, dynamic_model_selection, state_based_tool_selection

model = ChatOpenAI(model="gpt-5.4-mini")

agent = create_agent(
    model,
    tools=[define_meeting_parameters, save_sales_analysis, save_technical_analysis],
    state_schema=CustomAgentState,
    checkpointer=InMemorySaver(),
    middleware=[dynamic_prompt, dynamic_model_selection, state_based_tool_selection],
    response_format=Response,
    context_schema=CustomContext
)

def start_agent(transcript: str, duration_minutes: float, meeting_date: int):
    context = {"meeting_date": meeting_date, "duration_minutes": duration_minutes}

    response = agent.invoke(
        {"messages": [{"role": "user", "content": f"Analyse next transcript: {transcript}."}]},
        config={"configurable": {"thread_id": str(uuid4())}},
        context=CustomContext(**context),
    )

    return response
