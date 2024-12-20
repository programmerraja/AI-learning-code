import dspy
import os
from dotenv import load_dotenv

load_dotenv()
#
turbo = dspy.OllamaLocal(
    base_url="http://127.0.0.1:8080",
    model_type="chat"
)

dspy.settings.configure(lm=turbo)


class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


predict = dspy.Predict(GenerateAnswer)
# prediction = predict(question="how many hydrogent present in water", context="")
print(GenerateAnswer)

prediction = dspy.ChainOfThought("context, question -> answer")

pred = prediction(
    context="Which meant learning Lisp, since in those days Lisp was regarded as the language of AI.",
    question="What programming language did the author learn in college?",
)
print(pred.answer)
# turbo.inspect_history(n=10)
