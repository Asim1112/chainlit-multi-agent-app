import os
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import chainlit as cl

# Load environment
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini/gemini-2.0-flash"

# Define agents
web_dev_agent = Agent(
    name="WebDev",
    instructions="You are a professional web developer. Handle only website and web-related tasks.",
    model=LitellmModel(model=MODEL_NAME, api_key=API_KEY),
)

mobile_dev_agent = Agent(
    name="MobileDev",
    instructions="You are a skilled mobile app developer. Respond to tasks about mobile applications only.",
    model=LitellmModel(model=MODEL_NAME, api_key=API_KEY),
)

marketing_agent = Agent(
    name="MarketingAgent",
    instructions="You are an expert in marketing. Handle branding, social media, ad campaigns, and strategy.",
    model=LitellmModel(model=MODEL_NAME, api_key=API_KEY),
)

manager_agent = Agent(
    name="Manager",
    instructions="""
You are a smart manager. Based on the user's input, determine which agent (WebDev, MobileDev, or MarketingAgent) should handle the task.

Reply ONLY with the agent's name: WebDev, MobileDev, or MarketingAgent.
""",
    model=LitellmModel(model=MODEL_NAME, api_key=API_KEY),
)

@cl.on_message
async def main(message: cl.Message):
    user_input = message.content

    try:
        await cl.Message(content=f"You said: `{user_input}`").send()

        # Debug: Show API key
        if not API_KEY:
            await cl.Message(content="GEMINI_API_KEY not loaded.").send()
            return

        # Debug: Manager Agent is running
        await cl.Message(content="🔄 Asking Manager...").send()

        decision = await Runner.run(starting_agent=manager_agent, input=user_input)

        if not hasattr(decision, "final_output"):
            await cl.Message(content="Manager returned no output.").send()
            return

        chosen_agent = decision.final_output.strip()
        await cl.Message(content=f"Manager chose: **{chosen_agent}**").send()

        # Route to agent
        if chosen_agent == "WebDev":
            result = await Runner.run(starting_agent=web_dev_agent, input=user_input)
        elif chosen_agent == "MobileDev":
            result = await Runner.run(starting_agent=mobile_dev_agent, input=user_input)
        elif chosen_agent == "MarketingAgent":
            result = await Runner.run(starting_agent=marketing_agent, input=user_input)
        else:
            await cl.Message(content=f"Invalid agent selected: `{chosen_agent}`").send()
            return

        await cl.Message(content=f"**{chosen_agent}** says:\n{result.final_output}").send()

    except Exception as e:
        await cl.Message(content=f"Error occurred:\n`{str(e)}`").send()

