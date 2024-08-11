import dspy
from dspy.datasets.gsm8k import GSM8K, gsm8k_metric
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
import os

# 
# Set up the LM.
turbo = dspy.Google(
    # base_url="https://api.portkey.ai/v1/",
    model="gemini-1.5-flash-001",
    api_key="",
)
# from portkey_ai import Portkey

# portkey = Portkey(
#     api_key="",  # Replace with your Portkey API key
#     virtual_key="gemeni-2f24b9",  # Replace with your virtual key for Google
# )
dspy.settings.configure(lm=turbo)

article_summary = dspy.Example(
    article="This is an article.", summary="This is a summary."
).with_inputs("article")

input_key_only = article_summary.inputs()
non_input_key_only = article_summary.labels()

print("Example object with Input fields only:", input_key_only)
print("Example object with Non-Input fields only:", non_input_key_only)

trainset = [dspy.Example(report="LONG REPORT 1", summary="short summary 1"), ...]


# Metric
# A metric is just a function that will take examples from your data and take the output of your system,
# and return a score that quantifies how good the output is. What makes outputs from your system good or bad?


def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()


# Load math questions from the GSM8K dataset.
gsm8k = GSM8K()
gsm8k_trainset, gsm8k_devset = gsm8k.train[:10], gsm8k.dev[:10]


class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.prog(question=question)


config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

teleprompter = BootstrapFewShot(metric=gsm8k_metric, **config)
optimized_cot = teleprompter.compile(CoT(), trainset=gsm8k_trainset)


evaluate = Evaluate(
    devset=gsm8k_devset,
    metric=gsm8k_metric,
    num_threads=4,
    display_progress=True,
    display_table=0,
)

evaluate(optimized_cot)

turbo.inspect_history(n=1)


# predict = dspy.Predict("question->answer")

# prediction = predict(question="who i am")

# print(prediction.answer)

# turbo.inspect_history(n=1)
