from pathlib import Path

# Base directory
base_dir = Path(__file__).parent / "movie_recommender"

# Create directories
directories = [
    "core",
    "data",
    "api",
    "evaluation",
    "utils",
    "visualization"
]

# Create each directory and its __init__.py
for dir_name in directories:
    dir_path = base_dir / dir_name
    dir_path.mkdir(exist_ok=True, parents=True)
    
    # Create __init__.py in each directory
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        init_file.touch()

print("Directory structure created successfully!")
