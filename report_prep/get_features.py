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
