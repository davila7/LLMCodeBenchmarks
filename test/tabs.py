import streamlit as st
import json
from collections import defaultdict

# Load the JSON data
def load_data():
    with open('agents.json', 'r') as file:
        return json.load(file)

# Save the JSON data
def save_data(data):
    with open('agents.json', 'w') as file:
        json.dump(data, file, indent=2)

# Load initial data
data = load_data()

# Streamlit app
st.title('Agent Management System')

# Sidebar for adding new agent
with st.sidebar.expander("Add New Agent"):
    new_agent = {}
    new_agent['id'] = st.text_input("ID")
    new_agent['name'] = st.text_input("Name")
    new_agent['description'] = st.text_area("Description")
    new_agent['image'] = st.text_input("Image URL")
    new_agent['welcome'] = st.text_area("Welcome Message")
    new_agent['slug'] = st.text_input("Slug")
    new_agent['tools'] = st.text_input("Tools (comma-separated)").split(',')
    tags = st.text_input("Tags (comma-separated)")
    
    if st.button("Add Agent"):
        # Split tags and create a new agent for each tag
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        for tag in tag_list:
            agent_copy = new_agent.copy()
            agent_copy['tags'] = [tag]
            data.append(agent_copy)
        save_data(data)
        st.success(f"New agent added successfully with {len(tag_list)} tag(s)!")

# Create a dictionary to store agents by tag
agents_by_tag = defaultdict(list)

# Organize agents by tag
for agent in data:
    for tag in agent.get('tags', []):
        agents_by_tag[tag].append(agent)

# Create tabs for each tag
tabs = st.tabs(list(agents_by_tag.keys()))

# Display agents in each tab
for tab, tag in zip(tabs, agents_by_tag.keys()):
    with tab:
        st.header(tag.capitalize())
        
        # Create three columns
        cols = st.columns(3)
        
        # Distribute agents across the columns
        for i, agent in enumerate(agents_by_tag[tag]):
            with cols[i % 3]:
                with st.expander(agent['name']):
                    # Create a horizontal layout for image and name
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(agent['image'], width=50)
                    with col2:
                        st.subheader(agent['name'])
                    
                    st.write(f"**Description:** {agent['description']}")
                    st.write(f"**Welcome:** {agent['welcome']}")
                    st.write(f"**Slug:** {agent['slug']}")
                    st.write(f"**Tools:** {', '.join(agent['tools'])}")

# Add a search functionality
search_term = st.sidebar.text_input('Search agents')
if search_term:
    st.sidebar.header('Search Results')
    for agent in data:
        if search_term.lower() in agent['name'].lower() or search_term.lower() in agent['description'].lower():
            with st.sidebar.expander("Agent Info"):
                # Create a horizontal layout for image and name in search results
                col1, col2 = st.sidebar.columns([1, 3])
                with col1:
                    st.sidebar.image(agent['image'], width=50)
                with col2:
                    st.sidebar.subheader(agent['name'])
                
                st.sidebar.write(f"**Description:** {agent['description']}")
                st.sidebar.write(f"**Tags:** {', '.join(agent['tags'])}")
                st.sidebar.write(f"**Tools:** {', '.join(agent['tools'])}")

# Button to generate JSON and overwrite the file
if st.button("Generate JSON"):
    json_string = json.dumps(data, indent=2)
    st.code(json_string)  # Display the JSON string
    
    # Overwrite the agents.json file
    save_data(data)
    st.success("JSON generated and saved to agents.json")
