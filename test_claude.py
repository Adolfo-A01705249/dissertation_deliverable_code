import anthropic
import os

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY ")
client = anthropic.Anthropic(api_key=anthropic_api_key)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system="You are a network configuration assistant. Respond only with Cisco IOS extended name ACL scripts.",
    messages=[
        {
            "role": "user",
            "content": "Please give me the commands to create an extended named ACL that denies all traffic to the address 65.122.19.33 and permits all other traffic"
        }
    ]
)
print(message.content)
