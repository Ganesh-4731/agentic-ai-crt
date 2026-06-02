from agno.agent import Agent
from agno.models.ollama import Ollama

model = Ollama("llama3.2:1b")
agent = Agent(
    name = "Diet Planner Coach",
    model = model,
    instructions = """
You are a personal diet planner coach.

Rules:
1. Help users to create personalized diet plans based on their preferences, dietary restrictions, and health goals.
2. Provide meal suggestions, recipes, and nutritional information to support users in making informed food choices.
3. Encourage users to maintain a balanced diet and make healthier food choices.
Otherwise say: "I can only help with diet planning and nutrition advice."

"""
)
print("Diet Planner")
print("="*50)

while True:
    user_input = input("You : ").strip()
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    response = agent.run(user_input)
    print("Agent : ")
    print(response.content)
    print("="*50)