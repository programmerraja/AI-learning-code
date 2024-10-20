import os
from crewai import Agent, Task, Crew
# import google.generativeai as genai
from langchain_openai import AzureChatOpenAI

# genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))

# llm = genai.GenerativeModel("gemini-1.5-flash-001")


# from langchain_google_genai import ChatGoogleGenerativeAI


# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     verbose=True,
#     google_api_key=os.getenv("GOOGLE_GEMENI_API_KEY"),
# )


# llm = AzureChatOpenAI(
#     openai_api_version="2024-04-01-preview",
#     deployment_name="gpt-4o-mini",
# )

reviewPrompt = open(
    "/home/boopathik/Documents/Personal Code/AI-learning-code/Agents/Prompts/review_prompt.md",
    "r",
).read()

reviewExample = open(
    "/home/boopathik/Documents/Personal Code/AI-learning-code/Agents/Prompts/review_examples.md",
    "r",
).read()

reviewCriteria = open(
    "/home/boopathik/Documents/Personal Code/AI-learning-code/Agents/Prompts/review_criteria.md",
    "r",
).read()

finalPrompt = reviewPrompt.replace("CRITERIA", reviewCriteria)

codereviewer = Agent(
    role="Senior full stack develper",
    goal="Review the code for best practice and optimization",
    backstory=finalPrompt,
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o-mini",
)


task = Task(
    description="Review the code for best practice and optimization",
    expected_output="""Reply me in a plain JSON "review": "" plse don't cover the json with ``json "review":"" ```""",
    agent=codereviewer,
)

my_crew = Crew(agents=[codereviewer], tasks=[task])

crew = my_crew.kickoff(inputs={"CODE": "console.log(hai)"})
