from swarm import Swarm, Agent

# Initialize the Swarm client
client = Swarm()

# Define the assistant agent
assistant_agent = Agent(
    name="Assistant Agent",
    instructions="You are a helpful assistant. Respond to user queries to the best of your ability.",
)

# Function to print messages nicely
def pretty_print_messages(messages):
    for message in messages:
        if message["content"] is None:
            continue
        print(f"{message['sender']}: {message['content']}")

# Initialize an empty list to store messages
messages = []

# Start the interaction loop
while True:
    user_input = input("> ")
    messages.append({"role": "user", "content": user_input})

    # Run the agent with the current messages
    response = client.run(agent=assistant_agent, messages=messages)
    messages = response.messages

    # Print the response messages
    pretty_print_messages(messages)
