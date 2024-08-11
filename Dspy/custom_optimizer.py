import dspy
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
import os

custom_dataset = [
    {
        "question": "What is the tallest mountain in the world?",
        "context": "Mount Everest is the tallest mountain in the world, standing at 8,848 meters.",
        "answer": "Mount Everest",
    },
]


custom_trainset = [
    dspy.Example(
        question=example["question"],
        context=example["context"],
        answer=example["answer"],
    ).with_inputs("question", "context", "answer")
    for example in custom_dataset
]


custom_devset = custom_trainset  # Reusing the same set for simplicity in this example

llm = dspy.Google(
    # base_url="https://api.portkey.ai/v1/",
    model="gemini-1.5-flash-001",
    api_key=os.getenv("GOOGLE_API_KEY"),
)
dspy.settings.configure(lm=llm)


class CustomQAModule(dspy.Signature):
    """Answer questions using provided context."""

    question = dspy.InputField()
    context = dspy.InputField()
    answer = dspy.OutputField(desc="A short factual answer")


class CustomQA(dspy.Module):
    def __init__(self):
        super().__init__()

        self.generate_answer = dspy.ChainOfThought(CustomQAModule)

    def forward(self, question, context, answer):
        # print(question, "question", context, "question")
        prediction = self.generate_answer(question=question, context=context)
        return dspy.Prediction(answer=prediction.answer)


def validate_answer(example, pred, trace=None):
    return dspy.evaluate.answer_exact_match(example, pred)


optimizer = BootstrapFewShotWithRandomSearch(metric=validate_answer)

# Compile the CustomQA model with the optimizer
optimized_custom_qa = optimizer.compile(CustomQA(), trainset=custom_trainset)

optimized_custom_qa.save("./com.json")

test_question = "What is the tallest mountain in the world?"
test_context = (
    "Mount Everest is the tallest mountain in the world, standing at 8,848 meters."
)
print(llm.inspect_history(n=1000))
# Get the prediction from the optimized model
# pred = optimized_custom_qa(question=test_question, context=test_context)

# Print the answer
# print(f"Question: {test_question}")
# print(f"Context: {test_context}")
# print(f"Predicted Answer: {pred.answer}")
