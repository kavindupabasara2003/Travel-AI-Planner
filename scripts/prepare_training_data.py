
import pandas as pd
import json
import random

def create_instruction_dataset(csv_path, output_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Fill NaN values
    df = df.fillna("")
    
    dataset = []
    
    print("Generating Q&A pairs...")
    for _, row in df.iterrows():
        name = row['Location_Name']
        city = row['Located_City']
        address = row['Location']
        loc_type = row['Location_Type']
        context = row['AI_Context']
        
        # 1. Direct Recommendation Query
        prompts = [
            f"Recommend a {loc_type} in {city}.",
            f"Where can I find a good {loc_type} in {city}?",
            f"I'm visiting {city}, any {loc_type} suggestions?",
            f"Tell me about {name}.",
            f"What is {name}?"
        ]
        
        user_query = random.choice(prompts)
        
        # 2. Detailed Answer
        if "Tell" in user_query or "What" in user_query:
            answer = f"{context}"
        else:
            answer = f"You should check out {name}. {context}"

        # Llama 3 Chat Format
        entry = {
            "messages": [
                {"role": "system", "content": "You are a helpful Sri Lanka Travel Assistant."},
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": answer}
            ]
        }
        dataset.append(entry)
        
        # 3. Augmentation: "Where is X?"
        entry_loc = {
            "messages": [
                 {"role": "system", "content": "You are a helpful Sri Lanka Travel Assistant."},
                 {"role": "user", "content": f"Where is {name} located?"},
                 {"role": "assistant", "content": f"{name} is located at {address} in {city}."}
            ]
        }
        dataset.append(entry_loc)

    print(f"Created {len(dataset)} training examples.")
    
    with open(output_path, 'w') as f:
        for entry in dataset:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    create_instruction_dataset("data/SriLanka_Travel_Dataset_Final.csv", "data/srilanka_travel_chat.jsonl")
