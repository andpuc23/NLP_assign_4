# %% [markdown]
# ### Assignment 4 Part 4a

# %%
# Import the pandas library for data manipulation
import pandas as pd

# %%
# Check the file structure of the files dev.conll and dev.gold.conll
def read_first_lines(file_path, num_lines=5):
    with open(file_path, 'r') as file:
        for _ in range(num_lines):
            print(file.readline().strip())

# Paths to your files
dev_gold_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/data/dev.gold.conll'
dev_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/data/dev.conll'

print("Contents of dev.gold.conll:")
read_first_lines(dev_gold_path)
print("\nContents of dev.conll:")
read_first_lines(dev_path)

# %%
# Data preparation and analysis readiness
# Function to load CONLL files
def load_conll(file_path):
    """
    Load a CONLL formatted file and convert it into a pandas DataFrame.

    Parameters:
    file_path (str): The path to the CONLL file.

    Returns:
    DataFrame: A pandas DataFrame containing the data from the CONLL file.
    """

    # Store each row of data from the CONLL file
    data = []

    # Open en read files and return each row to data-list
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                # Split each line by tab and add to data list
                columns = line.strip().split('\t')
                data.append(columns)

    # Convert the list of data into a DataFrame with the stated column headers
    return pd.DataFrame(data, columns=["ID", "Form", "Lemma", "POS", "XPOS", "Morph", "Head", "DepRel", "Deps", "Misc"])


# %%
# Load the parser output and gold standard data
parser_output_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/data/dev.conll'
dev_gold_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/data/dev.gold.conll'

# Load the data into DataFrames
parser_output = load_conll(parser_output_path)
gold_standard = load_conll(dev_gold_path)


# A know error introduced to validate the working of the code:
# parser_output.at[0, 'Head'] = '2'  

# The code does fetch the known error but not the one in line 940. Additional analysis is required here.

# Display the first few rows of the loaded data for verification
print("Parser Output DataFrame:")
print(parser_output.head(), '\n')  
print("\nGold Standard DataFrame:")
print(gold_standard.head(), '\n')

# Analyse the manually found error in line 940
print("\nChecking specific lines around 940:")
print(parser_output.iloc[938:942])
print(gold_standard.iloc[938:942], '\n')

print("\nParser output shape:", parser_output.shape)
print("Gold standard shape:", gold_standard.shape, '\n')


# %%
# Function to compare the parser output to the gold standard and identify errors
def compare_parses(parser_output, gold_standard):
    """
    Compare the parser output to the gold standard and identify parsing errors.

    Parameters:
    parser_output (DataFrame): DataFrame containing the parser's output.
    gold_standard (DataFrame): DataFrame containing the gold standard annotations.

    Returns:
    list: A list of dictionaries containing details about each identified error.
    """
    errors = []
    for i, row in parser_output.iterrows():
        gold_row = gold_standard.iloc[i]
        # Check if the head or dependency relation is different between the parser output and the gold standard
        if row["Head"] != gold_row["Head"] or row["DepRel"] != gold_row["DepRel"]:
            # Determine the type of error
            error_type = determine_error_type(row, gold_row)
            errors.append({
                "sentence_id": row["ID"],
                "error_type": error_type,
                "incorrect_dependency": (row["Form"], row["DepRel"], row["Head"]),
                "correct_dependency": (gold_row["Form"], gold_row["DepRel"], gold_row["Head"]),
                "explanation": f"Incorrect attachment of {row['Form']}."
            })
            # Debugging-print to show that an error was found
            print(f"Error found in sentence ID {row['ID']}: {error_type}")
        else:
            # Debugging-print to show comparison details
            print(f"Match found in sentence ID {row['ID']}: {row['Form']} -> Head: {row['Head']}, DepRel: {row['DepRel']}")
    return errors

# %%
# Function to determine the type of parsing error
def determine_error_type(parsed_row, gold_row):
    """
    Determine the type of parsing error.

    Parameters:
    parsed_row (Series): A row from the parser output DataFrame.
    gold_row (Series): A row from the gold standard DataFrame.

    Returns:
    str: A string indicating the type of parsing error.
    """
    # Logic to determine the type of error based on dependency relations
    # Prepositional Phrase Attachment Error: e.g., "IN" (preposition) attached to wrong head
    if parsed_row['POS'] == 'IN' and parsed_row['DepRel'] == 'case' and gold_row['DepRel'] == 'nmod':
        return "Prepositional Phrase Attachment Error"
    
    # Verb Phrase Attachment Error: e.g., "VBG" (verb, gerund/present participle) attached to wrong head
    if parsed_row['POS'].startswith('V') and parsed_row['DepRel'].startswith('acl') and gold_row['DepRel'].startswith('advcl'):
        return "Verb Phrase Attachment Error"
    
    # Modifier Attachment Error: e.g., "RB" (adverb) or "JJ" (adjective) attached to wrong head
    if parsed_row['POS'] in ['RB', 'JJ'] and parsed_row['DepRel'].endswith('mod') and gold_row['DepRel'].endswith('advmod'):
        return "Modifier Attachment Error"
    
    # Coordination Attachment Error: e.g., "CC" (coordinating conjunction) attached to wrong head
    if parsed_row['POS'] == 'CC' and parsed_row['DepRel'] == 'cc' and gold_row['DepRel'] == 'conj':
        return "Coordination Attachment Error"
    
    # Default error type if none of the above
    return "Unknown Attachment Error"


# %%
# Function to save errors to a text file
def save_errors_to_file(errors, file_path):
    """
    Save the identified errors to a text file.

    Parameters:
    errors (list): A list of dictionaries containing details about each identified error.
    file_path (str): The path to the output text file.
    """
    with open(file_path, 'w') as file:
        for error in errors:
            file.write(f"Sentence ID: {error['sentence_id']}\n")
            file.write(f"Error Type: {error['error_type']}\n")
            file.write(f"Incorrect Dependency: {error['incorrect_dependency']}\n")
            file.write(f"Correct Dependency: {error['correct_dependency']}\n")
            file.write(f"Explanation: {error['explanation']}\n\n")

# Load the parser output and gold standard data
parser_output_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/data/dev.conll'
gold_standard_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/data/dev.gold.conll'

# Load the data into DataFrames
parser_output = load_conll(parser_output_path)
gold_standard = load_conll(gold_standard_path)

# Optionally revert the known error for full analysis
# parser_output.at[0, 'Head'] = '2'  

# Display the first few rows of the loaded data for verification
print("Parser Output DataFrame:")
print(parser_output.head())  # Display more rows for verification
print("\nGold Standard DataFrame:")
print(gold_standard.head())

# Compare the parser output to the gold standard and classify errors
errors = compare_parses(parser_output, gold_standard)

# Add a test error to ensure the file gets filled correctly
test_error = {
    "sentence_id": "9998",
    "error_type": "Test Error",
    "incorrect_dependency": ("test_word", "test_deprel", "test_head"),
    "correct_dependency": ("correct_word", "correct_deprel", "correct_head"),
    "explanation": "This is a test error to ensure the file gets filled correctly."
}
errors.append(test_error)

# Print the identified errors in a structured format
if errors:
    print("\nDocumenting Identified Errors:")
    for error in errors:
        print(f"Sentence ID: {error['sentence_id']}")
        print(f"Error Type: {error['error_type']}")
        print(f"Incorrect Dependency: {error['incorrect_dependency']}")
        print(f"Correct Dependency: {error['correct_dependency']}")
        print(f"Explanation: {error['explanation']}\n")
else:
    print("No errors found.")

# Save errors to a text file
output_file_path = '/Users/shirbaz/Documents/Master BA/NLP_A4_REPO/NLP_assign_4/utils/errors_documentation.txt'
save_errors_to_file(errors, output_file_path)

# %% [markdown]
# 


