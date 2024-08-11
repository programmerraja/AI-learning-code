from datasets import load_dataset
import dspy
import pandas as pd
import os

# Load the dataset
dataset = load_dataset("eelang/dsp_examples")


turbo = dspy.Google(
    # base_url="https://api.portkey.ai/v1/",
    model="gemini-1.5-flash-001",
    api_key="",
)
dspy.settings.configure(lm=turbo)

df = pd.DataFrame.from_dict(dataset["train"])

# Replace \n with " " in the Content column
df["Content"] = df["Content"].apply(lambda x: x.replace("\n", " "))

# Create a list of all the email categories
categories = list(df["Class"].unique())


# Build a DSPy simple signature
class EmailCategorizer(dspy.Signature):
    """A basic classifier of emails"""

    email = dspy.InputField(desc="an email message")
    category = dspy.OutputField(desc=f"one item in the following list: {categories}")


# Look at the dataframe
print(len(df))
df.head(10)

# The data is ordered in such a way we can split it in half to create a demonstration set, and a test set.
# I originally wanted to sample from the demonstration to help resolve the problem of the test set.
# Later on, It turned out this wasn't necessary at all.

demo_df = df[:5]
test_df = df[5:]

# Transform the example from their pandas format to a DSPy data type, and store the examples in teir appropriate lists
demos = []
tests = []
for i in range(5):
    demo_datum = demo_df.iloc[i]
    demo_example = dspy.Example(
        email=demo_datum["Content"], category=demo_datum["Class"]
    )
    demos.append(demo_example)

    test_datum = test_df.iloc[i]
    test_example = dspy.Example(
        email=test_datum["Content"], category=test_datum["Class"]
    )
    tests.append(test_example)

# Create a DSPy predictor, without using teleprompting at this stage
email_categorizer = dspy.Predict(EmailCategorizer)

# Create an empty list to store the predictions results
results = []

# Loop through the items in the test list. For each item, Ask the LM to provide a prediction
# Then compare the result of the prediction with ground truth.
# Store this in a list called "results" as boolean, and finally counter the % success.

for i in range(5):
    pred = email_categorizer(email=tests[i].email)
    truth = tests[i].category
    results.append(pred.category == truth)
print(sum(results) / len(results))

# View the LM History
turbo.inspect_history(n=10)

