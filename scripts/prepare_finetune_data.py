import csv
import json
import random
from pathlib import Path

# Config
INPUT_FILE = Path("data/SriLanka_Travel_Dataset_Final.csv")
OUTPUT_FILE = Path("data/train.jsonl")

# LLaMA 3 Instruct Protocol
def format_llama3(user_text, assistant_text):
    return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{assistant_text}<|eot_id|>"

def main():
    print(f"Reading from {INPUT_FILE}...")
    
    data = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract fields
            name = row.get('Location_Name', '').strip()
            city = row.get('Located_City', '').strip()
            ltype = row.get('Location_Type', '').strip()
            context = row.get('AI_Context', '').strip()
            
            if not name or not context:
                continue

            # Template 1: Direct Inquiry
            prompts_direct = [
                f"Tell me about {name}.",
                f"What is {name} in {city}?",
                f"Give me details on {name}.",
            ]
            
            # Template 2: Recommendation (if city and type exist)
            prompts_recommend = []
            if city and ltype:
                prompts_recommend = [
                    f"Suggest a {ltype} in {city}.",
                    f"I'm visiting {city}, any good {ltype}?",
                    f"Where can I find a {ltype} near {city}?",
                ]

            # Generate multiple examples per row to augment data
            # 1. Direct Inquiry Example
            user_msg = random.choice(prompts_direct)
            text = format_llama3(user_msg, context)
            data.append({"text": text})

            # 2. Recommendation Example (50% chance to avoid duplicates if sparse)
            if prompts_recommend and random.random() > 0.3:
                user_msg = random.choice(prompts_recommend)
                assistant_msg = f"I recommend visiting {name}. {context}"
                text = format_llama3(user_msg, assistant_msg)
                data.append({"text": text})

    # Shuffle to mix cities/types
    random.shuffle(data)
    
    # Split into Train (90%) and Validation (10%)
    split_idx = int(len(data) * 0.9)
    train_data = data[:split_idx]
    valid_data = data[split_idx:]
    
    # Save to JSONL
    print(f"Writing {len(train_data)} training examples to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in train_data:
            f.write(json.dumps(entry) + '\n')
            
    valid_file = Path("data/valid.jsonl")
    print(f"Writing {len(valid_data)} validation examples to {valid_file}...")
    with open(valid_file, 'w', encoding='utf-8') as f:
        for entry in valid_data:
            f.write(json.dumps(entry) + '\n')
            
    print("Done!")

if __name__ == "__main__":
    main()
