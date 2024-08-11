from dspy.teleprompt import MIPROv2
import dspy.evaluate
from dspy.datasets import HotPotQA


import dspy

llm = dspy.Google(
    # base_url="https://api.portkey.ai/v1/",
    model="gemini-1.5-flash-001",
    api_key="",
)

print("LLM test response:", llm("hello there"))

colbertv2_wiki17_abstracts = dspy.ColBERTv2(
    url="http://20.102.90.50:2017/wiki17_abstracts"
)
dspy.settings.configure(lm=llm, rm=colbertv2_wiki17_abstracts)


# Load the dataset.
dataset = HotPotQA(
    train_seed=1, train_size=32, eval_seed=2023, dev_size=50, test_size=0
)

# Tell DSPy that the 'question' field is the input. Any other fields are labels and/or metadata.
trainset = [x.with_inputs("question") for x in dataset.train]
devset = [x.with_inputs("question") for x in dataset.dev]

len(trainset), len(devset)


class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)


dev_example = devset[18]
print(f"[Devset] Question: {dev_example.question}")
print(f"[Devset] Answer: {dev_example.answer}")
print(f"[Devset] Relevant Wikipedia Titles: {dev_example.gold_titles}")

generate_answer = RAG()

pred = generate_answer(question=dev_example.question)

# Print the input and the prediction.
print(f"[Prediction] Question: {dev_example.question}")
print(f"[Prediction] Predicted Answer: {pred.answer}")


# Define our metric validation
def validate_context_and_answer(example, pred, trace=None):
    answer_EM = dspy.evaluate.answer_exact_match(example, pred)
    answer_PM = dspy.evaluate.answer_passage_match(example, pred)
    return answer_EM and answer_PM


# Set up a MIPROv2 optimizer, which will compile our RAG program.
optimizer = MIPROv2(
    metric=validate_context_and_answer,
    prompt_model=llm,
    task_model=llm,
    num_candidates=2,
    init_temperature=0.7,
)

# Initialize langwatch for this run, to track the optimizer compilation

# Compile
compiled_rag = optimizer.compile(
    RAG(),
    trainset=trainset,
    num_batches=10,
    max_bootstrapped_demos=3,
    max_labeled_demos=5,
    eval_kwargs=dict(num_threads=16, display_progress=True, display_table=0),
)

compiled_rag.save("./optimized_model.json")
