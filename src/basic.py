from agents import Agent, Runner
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# pytohn agent
agent = Agent(
  name="python-agent",
  instructions="You are an expert Python programming language"
)
response = Runner.run_sync(agent, "How to make for loop in Python?")
print(f"Instruction: {response.input}\n{response.final_output} ")