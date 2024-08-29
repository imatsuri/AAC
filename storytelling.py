from words_remove import remove_by_GPT
import pickle as pl
import itertools
from openai import OpenAI
import datetime
import os
import pdb
import json
import re

system_description = "You will be provided with the \"Research Word List\". Your task is to write narratives using only the words from the provided Research Word List. No additional words and grammatical modifications are allowed. The more different words used in a sentence, the higher the score. The more detailed information in a sentence, the higher the score. The more different ways of saying it, the higher the score. Each sentence should be 20 words or fewer."
prompt_storytelling = "Your task is to write narratives using only the words from the Research Words List.\nThese are definitions of narrative.\n-Sharing personal experiences that should explain an event's who, what, why, when, where, and how while also being able to share some of your emotions.\n-Each narrative should be at least 5-6 sentences long, and Each sentence should be 20 words or fewer. \n-Each narrative includes five elements: the setting, problem, emotion, action, and ending for example, \"I was playing cards with my brother(setting). My brother won the game(problem) and I got mad(emotion). So I asked him, \"Can you play again?\"(action) This time I won and I was happy. (ending)\"\n-The narratives should be on different topics, such as school, weekends, or something that irritated me.\nCan you write 5 narratives like talking to your friends? Follow these rules to write narratives.\n[rule]\n-ONLY use words from the research word list.\n-Avoid grammatical modifications like verb endings (-ed, -ing) and use the word as it appears in the list. It does not matter if the sentences are not grammatically correct. For example, you can not change the \"give\" to \"gives\" or \"gave\", even if it is grammatically correct.\n-The word list has phrases such as \"I'm hungry\" or \"I can't find what I want to say\". Use phrases directly from the list without changing form or splitting phrases.\n-The sentences don't have to be grammatically correct if you can't generate correct sentences with the words on the list. For example, if the list contains only {'dad', 'play', 'soccer', 'yesterday', 'park'}, \"Dad play soccer park yesterday\" is good to show \"my dad played soccer at a park yesterday\".\n-The more different words used in a sentence, the higher the score.\n-The more different ways of saying it, the higher the score. For example, \"I want you to open the window\" and \"Please open the window\" mean the same thing but are said in different ways."

def interleave_dict_values(pklfile):
    with open(pklfile, 'rb') as f:
        category = pl.load(f)
    # Making iterator to get a elements form each category 
    iterators = [iter(lst) for lst in category.values()]
    result = []
    # Extract elements in order from each iterator and arrange them alternately.
    for item in itertools.zip_longest(*iterators, fillvalue=''):
        result.extend(item)
    #remove duplicated symbols
    tmp = dict.fromkeys([item for item in result if item]) 
    result = list(tmp)
    return result

def GPT(symbol_list, history_filename, past_out=None):
    #history to build the model
    model_history = [
    {"role": "system", "content": [{"text": system_description,"type": "text"}]},
    {"role": "user","content": [{"text": prompt_storytelling,"type": "text"}]},
    {"role": "user","content": [{"text": f'[research word list] \n {symbol_list}',"type": "text"}]}
    ]
    with open(history_filename, 'r', encoding="utf-8") as file:
        content = file.read()
        history = json.loads(content)
    #decide next prompt here
    if past_out:
        next_prompt = [
          {"role": "user",
           "content": [{"text": "Generate more narratives","type": "text"}]
          },
          {"role": "assistant",
           "content": [{"text": past_out, "type": "text"}]
          },
          {"role": "user",
           "content": [{"text": "Generate another 5 narratives","type": "text"}]
          },
        ]
    else:
        next_prompt = [
        {"role": "user",
        "content": [{"text": "Generate another 5 narratives", "type": "text"}]}
        ]
    #Call ChatGPT
    print(model_history + history + next_prompt)
    ahead = input("Do you want to use GPT? (Y/N) >>>")
    if ahead != "Y":
        print("stop generate")
        return None
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages= model_history + history + next_prompt,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0.3,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )
    return(response.choices[0].message)

def too_long(output):
    texts = [line[3:] for line in output.split("\n") if line != ""]
    remove_long = []
    too_long = []
    for sample in texts:
        flg = True
        for sentence in re.split('[.:;!?-]', sample):
            words = re.findall(r'\b\w+\b', sentence)
            if len(words) > 20:
                too_long.append(sample)
                flg = False
                continue
        if flg:
            remove_long.append(sample)
    with open("long.txt", 'a', encoding="utf-8") as f:
        f.write("\n".join(too_long))
    remove_long = '\n'.join(f"{i+1}. {text}" for i, text in enumerate(remove_long))
    return remove_long

def generate_sentences(symbol_list, folder, past_dataset=None):
    #pkl_file = folder + "/symbol_list.pkl"
    #now = datetime.datetime.now()
    #log_filename = "log/" + folder.split("/")[-1] + '/generate_'+ now.strftime('%m%d%Y_%H%M%S') + '.txt'
    #pdb.set_trace()
    #with open(log_filename, 'w', encoding="utf-8") as f:
    output = GPT(symbol_list, folder+"/history.txt", past_dataset)
    output = output.content.replace("\n\n", "\n")
    print(output)
    valid_output = too_long(output)
    fix_output, final_data = remove_by_GPT(folder, valid_output)
    dataset = final_data.copy()
    if past_dataset:
        past_dataset = [sample[3:] for sample in past_dataset.split('\n')]
        past_output = past_dataset + fix_output
    else:
        past_output = fix_output.copy()
    with open("result.txt","a") as f:
        f.write("\n".join(final_data))
    for n in range(5):
        print(f'{n+1} times generation')
        """
        f.write('\n'.join(f"{i+5}. {text}" for i, text in enumerate(past_output)))
        f.flush()
        os.fsync(f.fileno())
        pdb.set_trace()
        """
        past_str = '\n'.join(f"{i+5}. {text}" for i, text in enumerate(past_output))
        output = GPT(symbol_list, folder+"\history.txt", past_str)
        if not output:
            break
        output = output.content.replace("\n\n", "\n")
        print(output)
        valid_output = too_long(output)
        fix_output, final_data = remove_by_GPT(folder, valid_output)
        past_output += fix_output
        dataset += final_data
        with open("result.txt","a") as f:
            f.write("\n".join(final_data))
    print(dataset)
    return dataset

"""
def generate_sentences(symbol_list, prompt):
    Output = chatGPT_API()
    not_list = check_words_in_list(symbol_list, Output)

    for n in range(3):
        if  not_list == []:
            break
        prompt = "These words are not on the symbol_list. Replace them with the words on the list. " + str(not_list)
        Output = chatGPT_API()
        not_list = check_words_in_list(symbol_list, Output)
    if not_list != []:
"""

if __name__ == "__main__":
    folder = "Input/communikate20"
    symbol_list = interleave_dict_values(folder+"/symbol_list.pkl")
    dataset = generate_sentences(symbol_list, folder)
    with open('result\communicate20_2.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(dataset.strip()))
