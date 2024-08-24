import os


def encode_features(
    encodings_path,
    features_file_path,
    sample_name,
):

    # Construct the full path for VariableNames.txt
    variable_names_path = "feature_extraction/VariableNames.txt"

    # Ensure the VariableNames.txt file exists
    if not os.path.exists(variable_names_path):
        raise FileNotFoundError(f"{variable_names_path} does not exist.")

    # Step 1: Load the file containing the features
    with open(features_file_path, "r") as file:
        extracted_features = file.read().splitlines()

    # Step 2: Load the `VariableNames.txt` file and map features to indices
    variable_names = {}

    with open(variable_names_path, "r", encoding="utf-8") as file:
        for line in file:
            index, feature = line.split(";", 1)
            variable_names[feature.strip()] = int(index)

    # Step 3: Initialize a list of zeros
    num_features = 30970
    binary_vector = [0] * num_features

    # Step 4: Set corresponding indices to 1 for features found in `extracted.txt`
    for feature in extracted_features:
        if feature in variable_names:
            index = variable_names[feature]
            binary_vector[index - 1] = (
                1  # Subtract 1 to convert 1-based index to 0-based
            )

    # Step 5: Generate a unique file name using the original file name and current timestamp
    unique_file_name = f"{sample_name}_encoding.txt"
    output_file_path = os.path.join(encodings_path, unique_file_name)

    # Step 6: Write the result to the output file
    with open(output_file_path, "w") as file:
        for value in binary_vector:
            file.write(f"{value}\n")

    return output_file_path
