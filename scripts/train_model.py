import os
import sys
from mlx_lm import lora

# Configuration
# Using the 3B Instruct model as base
MODEL_NAME = "mlx-community/Llama-3.2-3B-Instruct-4bit" 
DATA_DIR = "data"
OUTPUT_DIR = "adapters"
TRAIN_ITERS = 500  # Adjust based on time/quality needs
BATCH_SIZE = 1
LORA_LAYERS = 8
LEARNING_RATE = 1e-4

def main():
    print(f"Starting Fine-Tuning on {MODEL_NAME}...")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Iterations: {TRAIN_ITERS}")
    
    # Arguments for mlx_lm.lora
    # We construct the equivalent of the CLI arguments
    args = [
        "--model", MODEL_NAME,
        "--train",
        "--data", DATA_DIR,
        "--batch-size", str(BATCH_SIZE),
        "--lora-layers", str(LORA_LAYERS),
        "--iters", str(TRAIN_ITERS),
        "--learning-rate", str(LEARNING_RATE),
        "--adapter-path", OUTPUT_DIR,
        "--save-every", "100",
        "--steps-per-eval", "100"
    ]
    
    # Hack to allow calling the main function of the library with our args
    # This is often cleaner than using subprocess for library calls if they support it, 
    # but mlx_lm.lora.main reads sys.argv. 
    # Let's use subprocess to be safe and standard.
    import subprocess
    
    cmd = [
        sys.executable, "-m", "mlx_lm.lora",
        "--model", MODEL_NAME,
        "--train",
        "--data", DATA_DIR,
        "--batch-size", str(BATCH_SIZE),
        "--num-layers", str(LORA_LAYERS),
        "--iters", str(TRAIN_ITERS),
        "--learning-rate", str(LEARNING_RATE),
        "--adapter-path", OUTPUT_DIR,
        "--save-every", "100"
    ]
    
    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print("\nTraining Complete!")
    print(f"Adapters saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
