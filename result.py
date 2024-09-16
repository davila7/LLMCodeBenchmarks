import os
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.json')]

def load_json_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def display_as_table(data):
    rows = []
    for entry in data:
        model = entry.get('model', '')
        for task in entry.get('task', []):
            rows.append({
                'Model': model,
                'Description': task.get('description', ''),
                'Generated Code': task.get('generated_code', ''),
                'Success': task.get('success', ''),
                'Message': task.get('message', ''),
                'Execution Time': task.get('execution_time', ''),
                'Response Time': task.get('response_time', '')
            })
    df = pd.DataFrame(rows)
    return df

def main():
    st.title("LLM Code Benchmarks")
    
    directory = 'results'
    json_files = list_json_files(directory)
    
    if not json_files:
        st.write("No JSON files found in the directory.")
        return
    
    file_index = st.selectbox("Select a JSON file to display:", range(len(json_files)), format_func=lambda x: json_files[x])
    
    if file_index is not None:
        filepath = os.path.join(directory, json_files[file_index])
        data = load_json_file(filepath)
        df = display_as_table(data)
        
        # Group by 'Model' and 'Success' and plot
        grouped_df = df.groupby(['Model', 'Success']).size().unstack(fill_value=0)
        
        tab1, tab2 = st.tabs(["Charts", "Results"])
        
        with tab1:
            fig, ax = plt.subplots(figsize=(10, 6))
            grouped_df = grouped_df.sort_index(ascending=False)
            grouped_df.plot(kind='bar', stacked=True, ax=ax)
            for p in ax.patches:
                ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
            ax.set_title('Success Level Distribution by Model')
            ax.set_xlabel('Model')
            ax.set_ylabel('Count')
            st.title("By number of tasks")
            st.pyplot(fig)

            percentage_df = grouped_df.div(grouped_df.sum(axis=1), axis=0) * 100
            fig, ax = plt.subplots(figsize=(10, 6))
            percentage_df.plot(kind='bar', stacked=True, ax=ax)
            for p in ax.patches:
                ax.annotate(f'{p.get_height():.2f}%', (p.get_x() * 1.005, p.get_height() * 1.005))
            ax.set_title('Success Level Distribution by Model (Percentage)')
            ax.set_xlabel('Model')
            ax.set_ylabel('Percentage')
            st.title("By percentage")
            st.pyplot(fig)
        
        with tab2:
            st.dataframe(df)

if __name__ == "__main__":
    main()
