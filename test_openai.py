from openai import OpenAI
import os

opena_api_key = os.environ.get("OPENAI_KEY")
client = OpenAI(api_key=opena_api_key)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system", 
            "content": "You are a network configuration assistant. Respond only with Cisco IOS extended name ACL scripts."},
        {
            "role": "user",
            "content": "Please give me the commands to create an extended named ACL that denies all traffic to the address 65.122.19.33 and permits all other traffic"
        }
    ]
)

print(completion.choices[0].message.content)