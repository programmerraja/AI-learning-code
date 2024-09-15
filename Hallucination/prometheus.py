from typing import Any, Dict, List, Tuple, Type
from haystack import component
from haystack.components.evaluators import LLMEvaluator
from haystack.components.builders import PromptBuilder
from tqdm import tqdm
from numpy import mean as np_mean


ABS_SYSTEM_PROMPT = (
    "You are a fair judge assistant tasked with providing clear, objective feedback based on "
    "specific criteria, ensuring each assessment reflects the absolute standards set for performance."
)


@component
class PrometheusLLMEvaluator(LLMEvaluator):
    def __init__(
        self,
        generator,
        template: str,
        inputs: List[Tuple[str, Type[List]]],
        progress_bar: bool = True,
    ):
        outputs = ["feedback", "score"]
        self.validate_init_parameters(inputs, outputs, [])
        self.inputs = inputs
        self.outputs = outputs

        self._builder = PromptBuilder(template=template)
        self._generator = generator
        self.progress_bar = progress_bar

        component.set_input_types(self, **dict(inputs))

    def _parse_output(self, output):
        feedback, _, score_str = output.rpartition("[RESULT]")
        feedback = feedback.rpartition("###Feedback: [/INST]")[-1].strip()
        score_str = score_str.strip()

        score = None
        if score_str.isdigit() and score_str in ["1", "2", "3", "4", "5"]:
            score = int(score_str)
        return feedback, score

    @component.output_types(
        score=float, individual_scores=List[float], feedbacks=List[str]
    )
    def run(self, **inputs) -> Dict[str, Any]:
        self.validate_input_parameters(dict(self.inputs), inputs)

        # inputs is a dictionary with keys being input names and values being a list of input values
        # We need to iterate through the lists in parallel for all keys of the dictionary
        input_names, values = inputs.keys(), list(zip(*inputs.values()))
        list_of_input_names_to_values = [dict(zip(input_names, v)) for v in values]

        individual_scores, feedbacks = [], []
        for input_names_to_values in tqdm(
            list_of_input_names_to_values, disable=not self.progress_bar
        ):
            partial_prompt = self._builder.run(**input_names_to_values)["prompt"]
            prompt = f"[INST] {ABS_SYSTEM_PROMPT}\n{partial_prompt} [/INST]"

            output = self._generator.run(prompt=prompt)["replies"][0]

            feedback, individual_score = self._parse_output(output)
            if individual_score is not None:
                individual_scores.append(individual_score)
            feedbacks.append(feedback)
        score = np_mean(individual_scores)

        return {
            "score": score,
            "individual_scores": individual_scores,
            "feedbacks": feedbacks,
        }


