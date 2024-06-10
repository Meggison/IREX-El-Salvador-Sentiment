import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
import time

json_schema = {
    "classification": "classification value between 1, 0, -1",
    "reasoning": "reasoning of the answer in 50 words",
    "keywords": "main spanish words or phrases from the tweet that helped with the reasoning",
}

llm = ChatOllama(
    model="llama3",
    format="json",
    keep_alive=-1, # keep the model loaded indefinitely
    temperature=0.1,
    max_new_tokens=512
    )

def update_message(input_tweet):
    messages = [
        HumanMessage(
            content="""You are an AI language model trained to analyze and classify tweets about El Salvador.
    Your job is to categorize each tweet into one of three categories based on its sentiment: 1 (positive), 0 (neutral), or -1 (negative) using a
    local Perspective from El salvador political scene.

    Guidelines:
    . 1 (Positive): The tweet expresses a positive sentiment, such as happiness, praise, or admiration.
    . 0 (Neutral): The tweet is neutral,. It may present facts, ask questions, or be generally balanced in tone or a statement or just mention a fact or a name.
    .-1 (Negative): The tweet expresses a negative sentiment, such as criticism, disappointment, or disapproval.

    Examples for Reference:

    1 (POS):
    . Tweet: "Dios lo bendiga por ser un gran ser humano."
    - Reasoning: The tweet is praising and expressing positive feelings towards someone.

    . Tweet: "Me encanta la humanidad de nuestro astronauta, un hombre con gran corazón."
    - Reasoning: The tweet shows love and admiration for the astronaut.

    . Tweet: "Dos grandes hombres haciendo historia. Gracias por todo."
    - Reasoning: The tweet appreciates the actions of two men, showing gratitude and positivity.

    0 (NEU):
    . Tweet: "Tweet Maria Alicia Alas Moreno "
    - Reasoning:The tweet states a fact about the need for a certain type of president without strong positive or negative sentiment.

    . Tweet: "Tweet Nuestros obstaculos son mentales"
    - Reasoning: The tweet presents a factual statement about the astronaut's activities without expressing an opinion.

    . Tweet: "¿Qué opinan sobre las últimas noticias del presidente?"
    - Reasoning: The tweet is asking a question and does not convey a positive or negative sentiment.

    -1 (NEG):
    . Tweet: "No estoy de acuerdo con las políticas actuales."
    - Reasoning: The tweet expresses disagreement with current policies, indicating a negative sentiment.

    . Tweet: "Es una vergüenza que esto esté sucediendo en nuestro país."
    - Reasoning: The tweet expresses disappointment and criticism about a situation in the country.

    . Tweet: "Las decisiones del presidente están dañando la economía."
    - Reasoning: The tweet criticizes the president's decisions, showing a negative sentiment about their impact on the economy."""
        ),
        HumanMessage(content=f"""Instructions:

        -Read the tweet below carefully.

        - Determine the sentiment expressed based on the content, using the following definitions and references:

        - Generate a Json output followin this pattern: {json_schema}"""),
        HumanMessage(
            content=f"""Tweet: {input_tweet}"""
        ),
    ]
    return messages

# Test response
input_tweet = "Pongase serio Nayib Bukele  no nos venga con esa ud bien save que nadie a salido al espacio"
messages = update_message(input_tweet)
prompt = ChatPromptTemplate.from_messages(messages)
print(prompt)
#converting the json schema to a string
dumps = json.dumps(json_schema, indent=2)
print()
chain = prompt | llm | JsonOutputParser()

response = chain.invoke({"schema": dumps})
print("Sample response: ")
print(response)

# Run for the final dataframe
df = pd.read_csv("sentiment_beto_sample_bukele_updated.csv")
# Run on 10 rows for now
df = df.sample(n=20, random_state=100).reset_index()

sentiment_output=[]
sentiment_reason=[]
# sentiment_keywords=[]
start_time = time.time()
for i,input_tweet in enumerate (df.loc[:,'Text']):
    messages = update_message(input_tweet)    
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | JsonOutputParser()
    response = chain.invoke({"schema": dumps})
    print("\n\n Response \n", response)
    sentiment_output.append(response['classification'])
    sentiment_reason.append(response['reasoning'])
    # sentiment_keywords.append(response['keywords'])

end_time = time.time()
print("total time: ", end_time - start_time)
# Concat results with selected columns to get a new dataframe
sentiment_llama_df = pd.concat([df,
                               pd.Series(sentiment_output), 
                               pd.Series(sentiment_reason),
                            #    pd.Series(sentiment_keywords)
                               ],
                              axis=1)
sentiment_llama_df.rename(columns={0: 'llama3_output', 
                                   1: 'llama3_reason',
                                #    2: 'llama3_keywords'
                                   }, inplace=True)

print(sentiment_llama_df[['Text', 'llama3_output', 'llama3_reason']])
sentiment_llama_df.to_csv("sentiment_sample_scored_llama3.csv")