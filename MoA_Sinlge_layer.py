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



async def run_llm(model):

  
  for sleep_time in [1,2,4]:
    try:
        response = await async_client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": user_prompt}],
                temperature=0.7,
                max_tokens=512,
            )
        # print(f"Received response: '{response.completion[0].message.content}' from model: {model}")  # Print the response
        break
    except together.error.RateLimitError as e:
          print(e)
          await asyncio.sleep(sleep_time)

  return response.choices[0].message.content



async def main():
  result = await asyncio.gather(*[run_llm(model) for model in reference_models])
  print(result)
  final = client.chat.completions.create(
      model = aggregator_model,
      messages = [
          {"role": "system", "content": aggreagator_system_prompt + "\n" + "\n".join([f"{i+1}. {str(element)}" for i , element in enumerate(result)])},
          {"role": "user", "content": user_prompt}
      ],stream=True
  )
      # Build the system message for the aggregator
  system_message = aggreagator_system_prompt + "\n" + "\n".join(
      [f"{i+1}. {str(element)}" for i, element in enumerate(result)]
  )
 # Create the full message list that goes to the aggregator
  aggregator_messages = [
      {"role": "system", "content": system_message},
      {"role": "user", "content": user_prompt},
  ]

  # 💬 Print the full aggregator messages
  print("\n====== Aggregator Messages ======")
  for msg in aggregator_messages:
      print(f"{msg['role'].upper()}: {msg['content']}")
  print("=================================\n")

  for chunck in final:
      print(chunck.choices[0].delta.content,end="",flush=True)
         # Print the final response



user_prompt = "who is sum 5+7+16"

import nest_asyncio
nest_asyncio.apply()
asyncio.run(main())

