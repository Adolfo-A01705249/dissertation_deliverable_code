def get_zscot_prompt(base):
    start = "Please give me the script for an extended named ACL "
    zscot = ". Let's think step by step."
    return ">" + start + base + zscot

def get_pc_prompts(base):
    pc_start = "Please help me figure out the script for an extended named ACL "
    first_prompt = pc_start + base + ". "
    
    filename = "pc prompts.txt"
    with open(filename, "r") as file:
       raw_prompt_text = file.read()

    pc_prompts = [prompt.strip() for prompt in raw_prompt_text.split("-")[1:]]
    pc_prompts[0] = first_prompt + pc_prompts[0]
    for i in range(len(pc_prompts)):
        pc_prompts[i] = ">" + pc_prompts[i]

    return "\n".join(pc_prompts)


short_start = "Script for an ACL "
    
def get_fs_prompts(base):
    filename = "fs prompts.txt"
    with open(filename, "r") as file:
       exemplars = file.read()

    return ">" + exemplars + short_start + base

def get_fscot_prompts(base):
    filename = "fscot prompts.txt"
    with open(filename, "r") as file:
        exemplars = file.read()

        return ">" + exemplars + short_start + base

def write_prompts(filename, prompts):
    print(f"{filename}:\n{prompts}\n")
    with open(filename, "w") as file:
        file.write(prompts)

with open('cases.txt', 'r') as file:
    for line in file:
        stripped_line = line.strip()

        if stripped_line and stripped_line[0].isdigit():
            words = stripped_line.split()
            num = int(words[0])
            first_two_len = len(words[0]) + len(words[1])
            
            base_prompt = stripped_line[first_two_len+2:]
            prompts = get_pc_prompts(base_prompt)
            filename = f"case_inputs/prompts_{num}_pc.txt"
            write_prompts(filename, prompts)