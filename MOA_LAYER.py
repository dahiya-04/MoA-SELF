!pip install together
import asyncio
import os
import together
from together import AsyncTogether, Together

client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))
async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))

reference_models = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "Qwen/Qwen2.5-72B-Instruct-Turbo",
    "Qwen/Qwen2.5-Coder-32B-Instruct"
    
]

aggregator_model = "Qwen/Qwen2.5-72B-Instruct-Turbo"
aggreagator_system_prompt = """You have been provided with a set of responses from various open-source models to the latest user query. Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of accuracy and reliability.
Responses from models:"""

def getFinalSystemPrompt(sysytem_prompt,results):
  return(sysytem_prompt + "\n" + "\n".join([f"{i+1}. {str(element)}" for i , element in enumerate(results)]))



async def run_llm2(model, prev_response=None):
 for sleep_time in [1,2,4]:
  try:
    message = ([{
        "role": "system",
        "content": getFinalSystemPrompt(user_prompt,prev_response)
    },
              {"role":"user","content":user_prompt } ]
             if prev_response
             else [{"role":"user","content":user_prompt } ]  )
    response = await async_client.chat.completions.create(model=model,messages=message,
              temperature=0.7,max_tokens=512,)
    print(f"Received response: '{response.choices[0].message.content}' from model: {model}")  # Print the response
    break
  except together.error.RateLimitError as e:
    print(e)
    await asyncio.sleep(sleep_time)
  return response.choices[0].message.content

async def main():
  results = await asyncio.gather(*[run_llm2(model) for model in (reference_models)])

  for _ in range(1,layer-1):
    results = await asyncio.gather(*[run_llm2(model,prev_response=results) for model in (reference_models)])

  finalStream = client.chat.completions.create(
      model = aggregator_model,
      messages = [
          {"role": "system", "content": getFinalSystemPrompt(aggreagator_system_prompt,results)},
          {"role": "user", "content": user_prompt}
      ],stream=True
  )
    # 💬 Print the full aggregator messages
  print("\n====== Aggregator Messages ======")
 
  for chunck in finalStream:
      print(chunck.choices[0].delta.content,end="",flush=True)


layer =3


import nest_asyncio
nest_asyncio.apply()
asyncio.run(main())
