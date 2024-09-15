
import dspy
import os
from dotenv import load_dotenv
import asyncio
import aiohttp
from cachetools import TTLCache
import logging
import json
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from dspy.evaluate.evaluate import Evaluate
from dspy.retrieve import Retrieve
from dspy.primitives.prediction import Prediction
import backoff
import nest_asyncio
from sentence_transformers import SentenceTransformer, util
from rouge import Rouge
import random
import openai
import io
from pydub import AudioSegment
from pydub.playback import play

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables and setup logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure DSPy
llm = dspy.OpenAI(
    model='gpt-3.5-turbo',
    api_key=os.environ['OPENAI_API_KEY'],
    max_tokens=2000
)
dspy.settings.configure(lm=llm)

# Configure the retrieval model
try:
    colbertv2_wiki17_abstracts = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
    dspy.settings.configure(rm=colbertv2_wiki17_abstracts)
    logging.info("Successfully configured ColBERTv2 retrieval model")
except Exception as e:
    logging.error(f"Failed to configure ColBERTv2 retrieval model: {e}")
    logging.warning("Falling back to default retrieval method")

class QueryScientificJargon(dspy.Module):
    def __init__(self):
        super().__init__()
        self.cache = TTLCache(maxsize=1000, ttl=3600)
        self.rate_limit = 1.0
        self.local_dictionary = {
            "Hypothetical induction": "A reasoning process where scientists propose hypotheses to explain observations.",
            "Open-domain": "Refers to data or questions that are not confined to a specific subject area.",
            "AI": "Artificial Intelligence; the simulation of human intelligence processes by machines.",
            "Personalized medicine": "A medical model that separates people into different groups—with medical decisions, practices, and/or products being tailored to the individual patient.",
            "Patient outcomes": "The results of medical treatment, including quality of life, side effects, and mortality rates.",
            "Marine biodiversity": "The variety of life in marine ecosystems, including the diversity of plants, animals, and microorganisms.",
            "Overfishing": "The removal of a species of fish from a body of water at a rate that the species cannot replenish, resulting in diminished fish populations.",
            "Climate change": "Long-term shifts in temperatures and weather patterns, primarily caused by human activities.",
            "Global warming": "The long-term heating of Earth's surface observed since the pre-industrial period due to human activities.",
        }

    async def forward(self, jargon_terms):
        jargon_definitions = {}

        async with aiohttp.ClientSession() as session:
            tasks = [self.get_jargon_definition(term, session) for term in jargon_terms]
            results = await asyncio.gather(*tasks)

        for term, definitions in results:
            jargon_definitions[term] = definitions

        return jargon_definitions

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def get_jargon_definition(self, term, session):
        if term in self.cache:
            return term, self.cache[term]

        logging.info(f"Querying for term: {term}")
        
        # Check local dictionary first
        if term.lower() in self.local_dictionary:
            self.cache[term] = {"local": self.local_dictionary[term.lower()]}
            return term, self.cache[term]

        definitions = {
            "scientific_sources": await self.query_scientific_sources(term, session),
        }

        # Remove None values
        definitions = {k: v for k, v in definitions.items() if v is not None}

        if not definitions:
            # Use GPT-3 as a fallback for definition
            definitions["gpt"] = await self.query_gpt(term)

        self.cache[term] = definitions
        return term, definitions

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def query_scientific_sources(self, term, session):
        try:
            await asyncio.sleep(self.rate_limit)  # Rate limiting
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"
            async with session.get(url, headers={"User-Agent": "ScienceHypothesisBot/1.0"}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('extract')
                else:
                    logging.warning(f"Scientific source returned status {response.status} for term {term}")
        except Exception as e:
            logging.error(f"Error querying scientific sources for {term}: {e}")
        return None

    async def query_gpt(self, term):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                prompt = f"Provide a brief definition for the term '{term}' in the context of scientific research:"
                response = dspy.Predict("term -> definition")(term=prompt).definition
                return response.strip()
            except Exception as e:
                logging.warning(f"Error querying GPT for {term} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logging.error(f"Failed to query GPT for {term} after {max_retries} attempts")
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

class HypothesisGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_hypothesis = dspy.ChainOfThought("observation, jargon_definitions, context, retrieved_passages -> reasoning, novel_hypothesis")

    def forward(self, observation, jargon_definitions, context, retrieved_passages):
        result = self.generate_hypothesis(
            observation=observation,
            jargon_definitions=jargon_definitions,
            context=context,
            retrieved_passages=retrieved_passages
        )
        return result.reasoning, result.novel_hypothesis

class ScientificHypothesisDiscovery(dspy.Module):
    def __init__(self, num_passages=5):
        super().__init__()
        self.query_jargon_dictionary = QueryScientificJargon()
        self.retrieve = dspy.Retrieve(k=num_passages)
        logging.info(f"Successfully initialized Retrieve module with k={num_passages}")

        # Initialize these as None, they will be set later
        self.identify_jargon = None
        self.identify_context = None
        self.hypothesis_generator = HypothesisGenerator()

        # Set up OpenAI client
        openai.api_key = os.environ['OPENAI_API_KEY']

    def forward(self, observation):
        if not all([self.identify_jargon, self.identify_context]):
            raise ValueError("Not all required modules have been set.")

        try:
            jargon_terms = self.identify_jargon(observation=observation).jargon_terms.strip().split(',')
            jargon_terms = [term.strip() for term in jargon_terms if len(term.strip().split()) <= 3]  # Limit to terms with 3 words or less
            logging.info(f"Identified jargon terms: {jargon_terms}")
        except Exception as e:
            logging.error(f"Error in identify_jargon: {e}")
            jargon_terms = []

        try:
            jargon_definitions = asyncio.run(self.query_jargon_dictionary(jargon_terms))
            logging.info(f"Retrieved jargon definitions: {json.dumps(jargon_definitions, indent=2)}")
        except Exception as e:
            logging.error(f"Error in query_jargon_dictionary: {e}")
            jargon_definitions = {}

        try:
            context = self.identify_context(observation=observation).context.strip()
            logging.info(f"Identified context: {context}")
        except Exception as e:
            logging.error(f"Error in identify_context: {e}")
            context = ""

        relevant_passages = self.retrieve_relevant_passages(observation)
        if not relevant_passages:
            logging.warning("No relevant passages retrieved. Using a generic passage.")
            relevant_passages = ["This is a generic passage to provide some context for hypothesis generation."]
        
        try:
            reasoning, hypothesis = self.hypothesis_generator(
                observation=observation,
                jargon_definitions=json.dumps(jargon_definitions),
                context=context,
                retrieved_passages=json.dumps(relevant_passages)
            )
            logging.info(f"Generated hypothesis: {hypothesis}")
            logging.debug(f"Reasoning: {reasoning}")
        except Exception as e:
            logging.error(f"Error in generate_hypothesis: {e}")
            reasoning = "Unable to generate reasoning due to an error."
            hypothesis = "Unable to generate a hypothesis at this time."

        return dspy.Prediction(
            observation=observation,
            jargon_definitions=jargon_definitions,
            context=context,
            reasoning=reasoning,
            hypothesis=hypothesis,
            retrieved_passages=relevant_passages
        )

    def retrieve_relevant_passages(self, observation):
        try:
            result = self.retrieve(observation)
            if hasattr(result, 'passages'):
                logging.info(f"Successfully retrieved {len(result.passages)} passages")
                return result.passages
            elif isinstance(result, list):
                logging.info(f"Successfully retrieved {len(result)} passages")
                return result
            elif hasattr(result, 'topk'):
                logging.info(f"Successfully retrieved {len(result.topk)} passages")
                return result.topk
            else:
                logging.warning(f"Unexpected return type from retrieve method: {type(result)}")
                return self.fallback_retrieval(observation)
        except Exception as e:
            logging.error(f"Error in retrieve method: {str(e)}")
            return self.fallback_retrieval(observation)

    def fallback_retrieval(self, observation):
        logging.warning("Using fallback retrieval method")
        keywords = observation.split()[:5]  # Use first 5 words as keywords
        fallback_passages = [
            f"Passage related to {' '.join(keywords)}...",
            "General scientific knowledge passage...",
            "Placeholder for relevant scientific context..."
        ]
        logging.info(f"Generated {len(fallback_passages)} fallback passages")
        return fallback_passages

    def validate_passages(self, passages):
        if not passages:
            return False
        if not isinstance(passages, list):
            return False
        if not all(isinstance(p, str) for p in passages):
            return False
        return True

    def transcribe(self, file_path):
        with open(file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return transcript.text

    def generate_voice_audio(self, text: str):
        response = openai.audio.speech.create(
            model="tts-1-hd", voice="shimmer", input=text, response_format="mp3"
        )
        return response.content

    def speak(self, text: str):
        audio_bytes = self.generate_voice_audio(text)
        audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        play(audio)

def generate_and_load_trainset(num_examples=20):
    observations = [
        "An increase in atmospheric CO2 correlates with a rise in global temperatures.",
        "Marine biodiversity is declining at an alarming rate due to overfishing.",
        "AI is increasingly being used in personalized medicine to predict patient outcomes.",
        # Add more scientific observations here
    ]
    
    hypotheses = [
        "Increasing atmospheric CO2 levels may enhance plant photosynthesis rates under certain conditions, potentially affecting food security.",
        "Overfishing might lead to a shift in marine ecosystems, favoring species with rapid reproduction cycles.",
        "AI-driven models could identify novel biomarkers for disease prediction and treatment customization.",
        # Add corresponding hypotheses here
    ]
    
    trainset = []
    for _ in range(num_examples):
        idx = random.randint(0, len(observations) - 1)
        example = dspy.Example(observation=observations[idx], hypothesis=hypotheses[idx])
        trainset.append(example.with_inputs('observation'))  # Specify 'observation' as input
    
    return trainset

def hypothesis_evaluation(example, pred, trace=None, frac=0.5):
    rouge = Rouge()
    model = SentenceTransformer('all-MiniLM-L6-v2')

    def normalize_text(text):
        return ' '.join(text.lower().split())

    def calculate_rouge(prediction, ground_truth):
        scores = rouge.get_scores(prediction, ground_truth)
        return scores[0]['rouge-l']['f']

    def calculate_semantic_similarity(prediction, ground_truth):
        embeddings1 = model.encode([prediction], convert_to_tensor=True)
        embeddings2 = model.encode([ground_truth], convert_to_tensor=True)
        return util.pytorch_cos_sim(embeddings1, embeddings2).item()

    prediction = normalize_text(pred.hypothesis)
    ground_truth = normalize_text(example.hypothesis)

    rouge_score = calculate_rouge(prediction, ground_truth)
    semantic_similarity = calculate_semantic_similarity(prediction, ground_truth)

    combined_score = (rouge_score + semantic_similarity) / 2

    logging.info(f"Evaluation scores - ROUGE-L: {rouge_score:.4f}, Semantic Similarity: {semantic_similarity:.4f}, Combined: {combined_score:.4f}")
    logging.info(f"Generated hypothesis: {prediction}")
    logging.info(f"Ground truth: {ground_truth}")

    return combined_score >= frac, combined_score  # Return both the boolean result and the actual score

def evaluate(compiled_module, devset):
    results = []
    scores = []
    for example in devset:
        pred = compiled_module(example.observation)
        result, score = hypothesis_evaluation(example, pred)
        results.append(result)
        scores.append(score)
    avg_score = sum(scores) / len(scores)
    logging.info(f"Average evaluation score: {avg_score:.4f}")
    return results, avg_score

# Main execution
if __name__ == "__main__":
    # Setup and compilation
    dataset = generate_and_load_trainset()
    trainset = dataset[:-5]  # Use all but last 5 examples as train set
    devset = dataset[-5:]  # Use last 5 examples as dev set

    # Define the modules
    modules = [
        ("identify_jargon", dspy.Predict("observation -> jargon_terms")),
        ("identify_context", dspy.Predict("observation -> context")),
        ("generate_hypothesis", HypothesisGenerator())
    ]

    # Create a new ScientificHypothesisDiscovery instance
    discovery_instance = ScientificHypothesisDiscovery()

    # Set the modules
    for name, module in modules:
        setattr(discovery_instance, name, module)

    # Set instructions separately
    discovery_instance.identify_jargon.instructions = "Identify scientific jargon or key terms in the following observation. Output only individual terms or short phrases, separated by commas."
    discovery_instance.identify_context.instructions = "Identify the relevant scientific context or domain for the given observation."
    discovery_instance.generate_hypothesis.generate_hypothesis.instructions = """
    Given the observation, jargon definitions, context, and retrieved passages:
    1. Analyze the observation and identify key scientific concepts and requirements.
    2. Review the jargon definitions and context to understand the specific domain knowledge needed.
    3. Examine the retrieved passages and extract relevant information.
    4. Reason step-by-step about how to construct a novel hypothesis.
    5. Synthesize the information into a clear, concise, and scientifically plausible hypothesis.
    6. Ensure the hypothesis directly addresses the observation and incorporates relevant jargon and context.
    7. Provide your step-by-step reasoning in the 'reasoning' output.
    8. Provide your final novel hypothesis in the 'novel_hypothesis' output.
    """

    teleprompter = BootstrapFewShotWithRandomSearch(
        metric=hypothesis_evaluation,
        num_candidate_programs=5,
        max_bootstrapped_demos=3,
        max_labeled_demos=10,
        max_rounds=2,
        num_threads=1,
        max_errors=10
    )

    try:
        compiled_discovery = teleprompter.compile(discovery_instance, trainset=trainset, valset=devset)
    except Exception as e:
        logging.error(f"Error during compilation: {e}")
        compiled_discovery = discovery_instance

    # Save the compiled program
    try:
        compiled_program_json = json.dumps(compiled_discovery.dump_state(save_field_meta=True), indent=2)
        with open("compiled_scientific_hypothesis_discovery.json", "w") as f:
            f.write(compiled_program_json)
        print("Program saved to compiled_scientific_hypothesis_discovery.json")
    except Exception as e:
        logging.error(f"Error saving compiled program: {e}")

    # Evaluate the compiled program
    try:
        results, avg_score = evaluate(compiled_discovery, devset)
        print("Evaluation Results:")
        print(f"Binary results: {results}")
        print(f"Average score: {avg_score:.4f}")
    except Exception as e:
        logging.error(f"Error during evaluation: {e}")
        print("An error occurred during evaluation. Please check the logs for details.")

    # Interactive loop
    while True:
        input_type = input("Enter 'text' for text input or 'voice' for voice input (or 'quit' to exit): ")
        
        if input_type.lower() == 'quit':
            break
        
        if input_type.lower() == 'voice':
            file_path = input("Enter the path to your audio file: ")
            try:
                observation = compiled_discovery.transcribe(file_path)
                print(f"Transcribed observation: {observation}")
            except Exception as e:
                logging.error(f"Error during transcription: {e}")
                print("An error occurred while transcribing the audio. Please try again.")
                continue
        else:
            observation = input("Enter an observation: ")
        
        try:
            prediction = compiled_discovery(observation)
            print(f"Observation: {prediction.observation}")
            print(f"Identified Jargon Terms:")
            for term, definitions in prediction.jargon_definitions.items():
                print(f"  - {term}:")
                for source, definition in definitions.items():
                    print(f"    {source}: {definition}")
            print(f"Identified Context: {prediction.context}")
            print(f"Reasoning:")
            print(prediction.reasoning)
            print(f"Hypothesis: {prediction.hypothesis}")
            print("Retrieved Passages:")
            for i, passage in enumerate(prediction.retrieved_passages, 1):
                print(f"Passage {i}: {passage[:200]}...")  # Print first 200 characters of each passage
            
            # Ask if the user wants voice output
            voice_output = input("Do you want to hear the hypothesis spoken? (yes/no): ")
            if voice_output.lower() == 'yes':
                compiled_discovery.speak(prediction.hypothesis)
        
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            print("An error occurred while processing the observation. Please try again.")
        
        print("\n" + "-"*50 + "\n")  # Add a separator between iterations

    print("Thank you for using ScientificHypothesisDiscovery. Goodbye!")

# Error handling and cleanup
if __name__ == "__main__":
    try:
        # Main execution block
        pass  # The main execution is already handled in the previous parts of the script
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
        print("An unexpected error occurred. Please check the logs for details.")
    finally:
        # Perform any necessary cleanup
        logging.info("Cleaning up resources...")
        # Add any cleanup code here, such as closing database connections or file handles
        logging.info("Cleanup complete. Exiting program.")

