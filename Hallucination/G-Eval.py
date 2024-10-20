import os
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.metrics import HallucinationMetric

import google.generativeai as genai

from deepeval.models.base_model import DeepEvalBaseLLM

from deepeval.metrics import SummarizationMetric

genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))


class AzureOpenAI(DeepEvalBaseLLM):
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        print("[generate] PROMPT", prompt)

        chat_model = self.load_model()
        return chat_model.generate_content(prompt).text

    async def a_generate(self, prompt: str) -> str:
        print("[a_generate] PROMPT", prompt)
        chat_model = self.load_model()
        res = chat_model.generate_content(prompt)
        return res.text

    def get_model_name(self):
        return "Custom Google Model"


custom_model = genai.GenerativeModel("gemini-1.5-flash-001")

gemini = AzureOpenAI(model=custom_model)

print(custom_model.generate_content("hai"))

correctness_metric = GEval(
    name="Correctness",
    criteria="Determine whether the actual output is factually correct based on the expected output.",
    # NOTE: you can only provide either criteria or evaluation_steps, and not both
    evaluation_steps=[
        "Check whether the facts in 'actual output' contradicts any facts in 'expected output'",
        "You should also heavily penalize omission of detail",
        "Vague language, or contradicting OPINIONS, are OK",
    ],
    model=gemini,
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)


test_case = LLMTestCase(
    input="The dog chased the cat up the tree, who ran up the tree?",
    actual_output="It depends, some might consider the cat, while others might argue the dog.",
    expected_output="The cat.",
)

# correctness_metric.measure(test_case)
# print(correctness_metric.score)
# print(correctness_metric.reason)


# G-Eval is a two-step algorithm that first generates a series of evaluation_steps using chain of thoughts (CoTs) based on the given criteria,
# before using the generated steps to determine the final score using the parameters presented in an LLMTestCase.
# When you provide evaluation_steps, the GEval metric skips the first step and uses the provided steps to determine the final score instead.


# This is the original text to be summarized
input = """
The 'coverage score' is calculated as the percentage of assessment questions
for which both the summary and the original document provide a 'yes' answer. This
method ensures that the summary not only includes key information from the original
text but also accurately represents it. A higher coverage score indicates a
more comprehensive and faithful summary, signifying that the summary effectively
encapsulates the crucial points and details from the original content.
"""

# This is the summary, replace this with the actual output from your LLM application
actual_output = """
The coverage score quantifies how well a summary captures and
accurately represents key information from the original text,
with a higher score indicating greater comprehensiveness.
"""

test_case = LLMTestCase(input=input, actual_output=actual_output)
metric = SummarizationMetric(
    threshold=0.5,
    model=gemini,
    assessment_questions=[
        "Is the coverage score based on a percentage of 'yes' answers?",
        "Does the score ensure the summary's accuracy with the source?",
        "Does a higher score mean a more comprehensive summary?",
    ],
)

# metric.measure(test_case)
# print(metric.score)
# print(metric.reason)


# HALLUCINATION

context = [
    "A man with blond-hair, and a brown shirt drinking out of a public water fountain."
]

actual_output = "A blond drinking water in public."

test_case = LLMTestCase(
    input="What was the blond doing?", actual_output=actual_output, context=context
)
metric = HallucinationMetric(threshold=0.5, model=gemini)

metric.measure(test_case)
print(metric.score)
print(metric.reason)

# or evaluate test cases in bulk
evaluate([test_case], [metric])
