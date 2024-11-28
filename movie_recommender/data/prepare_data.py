import pandas as pd
import numpy as np
import os

def load_platform_data(platform_name, file_path):
    """Load data from a specific platform and standardize format."""
    df = pd.read_csv(file_path)
    
    # Add platform identifier
    df['platform'] = platform_name
    
    # Create standardized content_id
    prefix = platform_name[:3].upper()
    df['content_id'] = df['show_id'].apply(lambda x: f"{prefix}_{x.split('_')[-1]}")
    
    return df

def prepare_combined_dataset():
    """Prepare and combine datasets from all platforms."""
    # Load data from each platform
    netflix_data = load_platform_data('netflix', 'data/netflix_titles.csv')
    amazon_data = load_platform_data('amazon', 'data/amazon_prime_titles.csv')
    disney_data = load_platform_data('disney', 'data/disney_plus_titles.csv')
    
    # Combine all datasets
    combined_data = pd.concat([netflix_data, amazon_data, disney_data], ignore_index=True)
    
    # Standardize duration format
    combined_data['duration_min'] = combined_data['duration'].str.extract('(\d+)').astype(float)
    mask = combined_data['duration'].str.contains('Season', na=False)
    combined_data.loc[mask, 'duration_min'] = combined_data.loc[mask, 'duration_min'] * 13 * 45
    
    # Save combined dataset
    output_path = os.path.join('data', 'combined', 'streaming_combined.csv')
    combined_data.to_csv(output_path, index=False)
    print(f"Combined dataset saved to {output_path}")
    
    return combined_data

def prepare_viewing_history():
    """Load and prepare viewing history data."""
    viewing_history = pd.read_csv(os.path.join('data', 'combined', 'viewing_history.csv'))
    
    # Ensure all required columns exist
    required_columns = ['user_id', 'content_id', 'watch_date', 'completion_percentage', 'rating']
    for col in required_columns:
        if col not in viewing_history.columns:
            if col == 'rating':
                viewing_history[col] = np.nan
            else:
                raise ValueError(f"Required column {col} missing from viewing history")
    
    return viewing_history

def main():
    """Main function to prepare all datasets."""
    print("Preparing combined streaming dataset...")
    combined_data = prepare_combined_dataset()
    
    print("\nPreparing viewing history...")
    viewing_history = prepare_viewing_history()
    
    print("\nDataset Statistics:")
    print(f"Total titles: {len(combined_data)}")
    print(f"Total viewing records: {len(viewing_history)}")
    print("\nPlatform distribution:")
    print(combined_data['platform'].value_counts())
    print("\nContent type distribution:")
    print(combined_data['type'].value_counts())

if __name__ == "__main__":
    main()
