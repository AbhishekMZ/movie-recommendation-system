import pandas as pd
import os
from dotenv import load_dotenv

def combine_streaming_data():
    # Load environment variables
    load_dotenv()
    
    try:
        # Read the streaming service CSV files
        amazon_df = pd.read_csv('amazon_prime_titles.csv')
        disney_df = pd.read_csv('disney_plus_titles.csv')
        netflix_df = pd.read_csv('netflix_titles.csv')
        
        # Add source column to each DataFrame
        amazon_df['source'] = 'AMAZON'
        disney_df['source'] = 'DISNEY'
        netflix_df['source'] = 'NETFLIX'
        
        # Create unique IDs for each service
        amazon_df['unique_id'] = 'AMZ_' + amazon_df.index.astype(str)
        disney_df['unique_id'] = 'DSN_' + disney_df.index.astype(str)
        netflix_df['unique_id'] = 'NFX_' + netflix_df.index.astype(str)
        
        # Ensure all DataFrames have the same columns
        common_columns = ['show_id', 'type', 'title', 'director', 'cast', 'country', 
                         'date_added', 'release_year', 'rating', 'duration', 'listed_in', 
                         'description', 'source', 'unique_id']
        
        # Standardize columns for each DataFrame
        for df in [amazon_df, disney_df, netflix_df]:
            for col in common_columns:
                if col not in df.columns and col not in ['source', 'unique_id']:
                    df[col] = None
        
        # Combine all DataFrames
        combined_df = pd.concat([amazon_df, disney_df, netflix_df], ignore_index=True)
        
        # Reorder columns
        combined_df = combined_df[common_columns]
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join('data', 'combined')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save combined dataset
        output_path = os.path.join(output_dir, 'streaming_combined.csv')
        combined_df.to_csv(output_path, index=False)
        
        print(f"Successfully created combined streaming data file: {output_path}")
        print(f"Total entries: {len(combined_df)}")
        print("\nEntries per streaming service:")
        print(combined_df['source'].value_counts())
        print("\nSample of combined data:")
        print(combined_df.head())
        
        # Create summary statistics
        print("\nSummary Statistics:")
        print(f"Total movies/shows: {len(combined_df)}")
        print(f"Movies: {len(combined_df[combined_df['type'] == 'Movie'])}")
        print(f"TV Shows: {len(combined_df[combined_df['type'] == 'TV Show'])}")
        print("\nContent by year:")
        print(combined_df['release_year'].value_counts().sort_index().tail())
        
    except FileNotFoundError as e:
        print("Error: Could not find one or more input files.")
        print("Please ensure the following files are present in the root directory:")
        print("- amazon_prime_titles.csv")
        print("- disney_plus_titles.csv")
        print("- netflix_titles.csv")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    combine_streaming_data()
