import kagglehub

# Download latest version
# path = kagglehub.dataset_download("gagandeep16/car-sales")

# print("Path to dataset files:", path)

import pandas as pd

# Load dataset
data_path = r"C:\Users\sam\.cache\kagglehub\datasets\gagandeep16\car-sales\versions\1\Car_sales.csv"
df = pd.read_csv(data_path)

# Basic exploration
print(df.head())
print(df.info())
print(df.describe())
