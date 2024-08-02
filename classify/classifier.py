import numpy as np
import pandas as pd
import joblib


class RansomwareClassifer:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    # model = joblib.load("svm_model.joblib")

    def read_data_from_file(self, file_path):
        with open(file_path, "r") as file:
            # Read all lines and convert to floats
            data = list(map(float, file.readlines()))

        # Convert the list to a pandas DataFrame
        num_features = self.model.n_features_in_
        df = pd.DataFrame(
            np.array(data).reshape(-1, num_features + 3)
        )  # Assuming 3 columns to be dropped

        # Add column headers
        df.columns = [f"col_{i}" for i in range(df.shape[1])]

        if "col_0" in df.columns:
            df.drop("col_0", inplace=True, axis=1)  # Drop IDs
        if "col_1" in df.columns:
            df.drop("col_1", inplace=True, axis=1)  # Drop Labels
        if "col_2" in df.columns:
            df.drop("col_2", inplace=True, axis=1)  # Drop Ransomware family

        return df

    def classify_sample(self, encoded_file_path):

        # Read data from the file containing encodings
        input_data = self.read_data_from_file(encoded_file_path)

        # Print the shape of the input data to verify
        print(f"Shape of input data: {input_data.shape}")

        predictions = self.model.predict(input_data)

        for i, prediction in enumerate(predictions):
            print("Prediction for sample {}: {}".format(i + 1, prediction))

        return prediction
