import os
import pandas as pd

# Define the folder path containing the CSV files
folder_path = 'result_records/'

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize an empty list to hold DataFrames
dfs = []

# Read each CSV file and append the DataFrame to the list
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    dfs.append(df)

# Concatenate all DataFrames into one
final_df = pd.concat(dfs, ignore_index=True)

# Optionally, save the concatenated DataFrame to a new CSV file
final_df.to_csv('result_records.csv', index=False)

# Display the concatenated DataFrame (optional)
print(final_df)
