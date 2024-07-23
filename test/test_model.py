import numpy as np
import pandas as pd
import joblib

model = joblib.load("svm_model.joblib")

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read all lines and convert to floats
        data = list(map(float, file.readlines()))
    
    # Convert the list to a pandas DataFrame
    num_features = model.n_features_in_
    df = pd.DataFrame(np.array(data).reshape(-1, num_features + 3))  # Assuming 3 columns to be dropped

    # Add column headers
    df.columns = [f'col_{i}' for i in range(df.shape[1])]

    if 'col_0' in df.columns:
        df.drop('col_0', inplace=True, axis=1)  # Drop IDs
    if 'col_1' in df.columns:
        df.drop('col_1', inplace=True, axis=1)  # Drop Labels
    if 'col_2' in df.columns:
        df.drop('col_2', inplace=True, axis=1)  # Drop Ransomware family

    return df

# Read data from the text file
input_data = read_data_from_file('test.txt')

# Print the shape of the input data to verify
print(f"Shape of input data: {input_data.shape}")

predictions = model.predict(input_data)

for i, prediction in enumerate(predictions):
    print("Prediction for sample {}: {}".format(i+1, prediction))
