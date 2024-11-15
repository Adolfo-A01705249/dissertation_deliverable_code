from fireworks.client import Fireworks
from openai import OpenAI
from nltk.translate.bleu_score import sentence_bleu
import os
import sys
import subprocess
import shutil
import pandas as pd
import re

SHOW_TOKENS = False
SAVE_CAMPION_LOGS = False

INPUTS_FOLDER = "case_inputs/"
INTERACTIONS_FOLDER = "interactions/"
LLM_ACLS_FOLDER = "llm_generated_acls/"
CAMPION_FOLDER = "campion_workplace/configs/"
CAMPION_LOGS_FOLDER = "campion_workplace/logs/"
BLEU_FOLDER = "bleu_inputs/"
RESULTS_FOLDER = "result_records/"

api_key = os.environ.get("FIREWORKSAI_KEY")
fireworks_client = Fireworks(api_key=api_key)

opena_api_key = os.environ.get("OPENAI_KEY")
openai_client = OpenAI(api_key=opena_api_key)

models = {
   #"mix": "mixtral-8x22b-instruct",
   #"llama3b": "llama-v3p2-3b-instruct",
   #"llama70b": "llama-v3-70b-instruct",
   "llama11b": "llama-v3p2-11b-vision-instruct",
   "llama90b": "llama-v3p2-90b-vision-instruct",
   "gpt4o": "gpt-4o",
   "gpt4omini": "gpt-4o-mini",
}

past_messages = None
def initialize_messages():
   global past_messages 
   past_messages = []
   system_message = {
  	   "role": "system",
  	   "content":
"""You are a helpful, respectful and honest network configuration assistant.
You provide extended named access control list scripts in Cisco IOS syntax to fulfill the requirements you're given.
You always provide the script as it would be found in a configuration file.
Make sure to use the syntax for *extended* and *named* access control lists.
Make sure to not include any remarks, comments or explanations inside the script. 
Make sure to not include any console navigation commands.
Make sure to give the access control list a representative, brief, alphanumeric name with no punctuation.
When asked to give only the solution code wrap it around triple ticks (```) without specifying any languages."""
   }
   past_messages.append(system_message)

def get_model_client(model):
   if model == models["gpt4o"] or model == models["gpt4omini"]:
      return openai_client
   else:
      return fireworks_client

def get_model_string(model):
   if model == models["gpt4o"] or model == models["gpt4omini"]:
      return model
   else:
      return f"accounts/fireworks/models/{model}"
   
def query_model(prompt, model): 
   latest_user_message = {"role": "user", "content": prompt,}
   past_messages.append(latest_user_message)

   response = get_model_client(model).chat.completions.create(
      model=get_model_string(model),
      messages=past_messages,
   )

   response_text = response.choices[0].message.content
   latest_model_message = {"role": "assistant", "content": response_text,}
   past_messages.append(latest_model_message)

   print(f"User prompt:\n{prompt}\n")
   print(f"The model's response:\n{response_text}\n")

   if SHOW_TOKENS:
      print(f"usage")
      print(f"-prompt tokens: {response.usage.prompt_tokens}")
      print(f"-completion tokens: {response.usage.completion_tokens}")
      print(f"-total tokens: {response.usage.total_tokens}\n")

def get_manual_acl_file_name(case_number):
   return f"acl_manual_{case_number}.txt"

def get_llm_acl_file_name(scenario_id):
   return f"acl_llm_{scenario_id}.txt"

def read_prompts(case_number, prompting_technique):
   filename = f"prompts_{case_number}_{prompting_technique}.txt"
   with open(INPUTS_FOLDER + filename, "r") as file:
      raw_prompt_text = file.read()

   prompts = [prompt.strip() for prompt in raw_prompt_text.split(">")[1:]]
   last_promp = "Now please give me only the solution as only one code snippet so I can store it in a configuration file (without explanations or any other text)"
   prompts.append(last_promp)
   return prompts

def save_messages(scenario_id):
   filename = f"interaction_{scenario_id}.txt"
   with open(INTERACTIONS_FOLDER + filename, "w") as file:
      system_prompt = past_messages[0]["content"]
      file.write(f"System prompt:\n{system_prompt}\n\n")
      
      for i in range(1, len(past_messages), 2):
         prompt = past_messages[i]["content"]
         response = past_messages[i+1]["content"]
         file.write(f"User prompt:\n{prompt}\n\n")
         file.write(f"The model's response:\n{response}\n\n")

def get_llm_acl_text():
   return past_messages[-1]["content"].strip(' \t\n\r\f\v`')

def save_llm_acl(scenario_id):
   last_model_response = get_llm_acl_text()
   filename = get_llm_acl_file_name(scenario_id)
   with open(LLM_ACLS_FOLDER + filename, "w") as file:
      file.write(last_model_response)

def copy_acls_into_campion(case_number, scenario_id):
   folder_manual = INPUTS_FOLDER
   filename_manual = get_manual_acl_file_name(case_number)

   folder_llm = LLM_ACLS_FOLDER
   filename_llm = get_llm_acl_file_name(scenario_id)
   
   shutil.copy(folder_manual + filename_manual, CAMPION_FOLDER + filename_manual)
   shutil.copy(folder_llm    + filename_llm,    CAMPION_FOLDER + filename_llm)

def get_acl_name(acl_text):
   acl_words = acl_text.split()
   sequence = ["ip", "access-list", "extended"]
   seq_length = len(sequence)
   
   name_index = -1
   for i in range(len(acl_words) - seq_length + 1):
      if acl_words[i:i + seq_length] == sequence:
         name_index = i + seq_length
         break

   if name_index < len(acl_words) and name_index != -1:
      return acl_words[name_index]
   
   return None

def match_acl_names(case_number):   
   llm_acl = get_llm_acl_text()
   llm_acl_name = get_acl_name(llm_acl)

   if llm_acl_name != None:
      filename = get_manual_acl_file_name(case_number)
      with open(CAMPION_FOLDER + filename, "r") as file:
         manual_acl = file.read()

      MANUAL_ACL_NAME = "list_name"
      manual_acl = manual_acl.replace(MANUAL_ACL_NAME, llm_acl_name)
      with open(CAMPION_FOLDER + filename, "w") as file:
         file.write(manual_acl)

      print(f"Y Renamed manual ACL to match LLM ACL: {llm_acl_name}")
      return True
   else:
      print("N Could NOT find LLM ACL name")
      return False

def clear_campion_space(case_number, scenario_id):
   filename_manual = get_manual_acl_file_name(case_number)
   filename_llm = get_llm_acl_file_name(scenario_id)
   shutil.move(CAMPION_FOLDER + filename_manual, BLEU_FOLDER + filename_manual)
   os.remove(CAMPION_FOLDER + filename_llm)
   
def save_campion_logs(campion_output, scenario_id):
   filename = f"log_{scenario_id}.txt"
   with open(CAMPION_LOGS_FOLDER + filename, "w") as file:
      file.write(campion_output)

def run_acl_comparison(scenario_id):
   current_folder = os.getcwd().replace("\\", "/")
   VENV_PYTHON = current_folder + "/.venv/Scripts/python.exe"
   CAMPION_SCRIPT = "run_diff.py"

   process = subprocess.Popen([VENV_PYTHON, CAMPION_SCRIPT, scenario_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   
   stdout, stderr = process.communicate()
   output = stdout.decode().rstrip()
   error = stderr.decode() # Campion sends normal messages to stderr too for some reason
   
   if "NO diff file created" in output:
      print(f"Y Campion: {output}")
   else:
      print(f"N Campion: {output}")

   if SAVE_CAMPION_LOGS:
      save_campion_logs(error, scenario_id)

   NO_DIFF_FILE_LINE = "NO diff file created"
   PARSE_ERROR_LINE = "Your snapshot was successfully initialized but Batfish failed to fully recognized some lines in one or more input files" 
   return (not NO_DIFF_FILE_LINE in output), (not PARSE_ERROR_LINE in error)

def get_manual_acl_text(case_number, folder):
   filename = get_manual_acl_file_name(case_number)
   with open(folder + filename, "r") as file:
      manual_acl = file.read()
   return manual_acl

def save_alternate_acl(acl_text, case_number):
   filename = f"acl_alternate_{case_number}.txt"
   with open(BLEU_FOLDER + filename, "w") as file:
      file.write(acl_text)

def get_alternate_acl(acl_text):
   alternate_acl = re.sub(r"(host) ([0-9\.]+)", r"\2 0.0.0.0", acl_text)
   alternate_acl = alternate_acl.replace("any", "0.0.0.0 255.255.255.255")

   port_numbers = {
      "ftp-data": 20,
      "ftp": 21,
      "telnet": 23,
      "www": 80,
      "https": 443,
   }

   for port_keyword in port_numbers.keys():
      alternate_acl = alternate_acl.replace(port_keyword, str(port_numbers[port_keyword]))

   return alternate_acl

def get_bleu_score(case_number):   
   manual_acl = get_manual_acl_text(case_number, BLEU_FOLDER)
   alternate_manual_acl = get_alternate_acl(manual_acl)
   save_alternate_acl(alternate_manual_acl, case_number)
   reference = [
      manual_acl.split(),
      alternate_manual_acl.split(),
   ]
   candidate = get_llm_acl_text().split()
   return sentence_bleu(reference, candidate)



# Configure run with command line arguments
# py run_scenario.py <model shorthand> <prompting technique> [{only case # | first case # last case #}]
# prompting technique = {zs, fs, zscot, fscot, pc}
# models = {llama3b, llama11b, gpt4o, gpt4omini}
case_total = 2
model_shorthand = sys.argv[1]
model = models[model_shorthand]
prompting_technique = sys.argv[2]
first_case_number = 1
last_case_number = case_total

if len(sys.argv) >= 4:
   first_case_number = int(sys.argv[3])
   last_case_number = first_case_number
   if len(sys.argv) == 5:
      last_case_number = int(sys.argv[4])



columns = ["Case number", "Prompting technique", "Model", "Matched", "Diff found", "Well formed", "Functionally equivalent", "BLEU score"]
records = pd.DataFrame(columns=columns)

for case in range(first_case_number, last_case_number + 1):
   case_number = case
   scenario_id = f"{case_number}_{prompting_technique}_{model}"
   print(f"\nRunning case with ID: {scenario_id}")
   print("--------------------------------")
   

   # ============ Querying the model API ============
   # Read prompts from file
   prompts = read_prompts(case_number, prompting_technique)

   # Query model with prompts
   initialize_messages()
   for prompt in prompts:
      query_model(prompt, model)

   # Save whole interaction to file
   save_messages(scenario_id)

   # Save last model response to file
   save_llm_acl(scenario_id)


   # ============ Running campion ============
   # Place manual and llm acls into campion folder
   copy_acls_into_campion(case_number, scenario_id)

   # Find llm acl name and give it to manual acl
   names_matched = match_acl_names(case_number)
   
   # Run campion
   diff_found, well_formed = run_acl_comparison(scenario_id)

   # Clear files from campion folder
   clear_campion_space(case_number, scenario_id)

   if well_formed:
      print("Y LLM ACL was well formed")
   else:
      print("N LLM ACL was NOT well formed")

   functionally_equivalent = (not diff_found) and well_formed and names_matched

   if functionally_equivalent:
      print("Y Manual and LLM ACLs are equivalent")
   else:
      print("N Manual and LLM ACLs are NOT equivalent")

   
   # ============ Getting BLEU score ============
   bleu_score = get_bleu_score(case_number)
   print(f"BLEU score is: {bleu_score}")



   record = {
      "Case number": case_number,
      "Prompting technique": prompting_technique,
      "Model": model,
      "Matched": names_matched,
      "Diff found": diff_found, 
      "Well formed": well_formed,
      "Functionally equivalent": functionally_equivalent,
      "BLEU score": bleu_score,
   }
   records.loc[len(records)] = record


filename = f"result_records_{first_case_number}-{last_case_number}_{prompting_technique}_{model}.csv"
records.to_csv(RESULTS_FOLDER + filename, index=False)