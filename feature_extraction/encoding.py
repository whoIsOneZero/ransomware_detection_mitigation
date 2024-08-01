# Step 1: Load the `extracted.txt` file
with open('extracted.txt', 'r') as file:
    extracted_features = file.read().splitlines()

# Step 2: Load the `VariableNames.txt` file and map features to indices
variable_names = {}
""" i = 0 """
with open('VariableNames.txt', 'r', encoding='utf-8') as file:
    for line in file:
        index, feature = line.split(';', 1)
        variable_names[feature.strip()] = int(index)

        """ if i < 5:
            print(feature)
            i = i + 1 """
        
# Step 3: Initialize a list of zeros
num_features = 30970
binary_vector = [0] * num_features

# Step 4: Set corresponding indices to 1 for features found in `extracted.txt`
for feature in extracted_features:
    if feature in variable_names:
        index = variable_names[feature]
        binary_vector[index - 1] = 1  # Subtract 1 to convert 1-based index to 0-based

# Step 5: Write the result to `preprocessed.txt`
with open('preprocessed.txt', 'w') as file:
    for value in binary_vector:
        file.write(f"{value}\n")