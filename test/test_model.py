import numpy as np
import joblib

model = joblib.load("svm_model.joblib")

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read all lines and convert to floats
        data = list(map(float, file.readlines()))
    
    # Convert the list to a NumPy array and reshape it
    num_features = model.n_features_in_
    data = np.array(data).reshape(-1, num_features)
    return data

# Read data from the text file
input_data = read_data_from_file('test.txt')

# Print the shape of the input data to verify
print(f"Shape of input data: {input_data.shape}")

predictions = model.predict(input_data)

for i, prediction in enumerate(predictions):
    print("Prediction for sample {}: {}".format(i+1, prediction))
