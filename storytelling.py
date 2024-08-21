from words_check import check_words_in_list
import pickle as pl
import itertools
from openai import OpenAI
import datetime
import os

system_description = "You will be provided with the \"Research Word List\". Your task is to write narratives using only the words from the provided Research Word List. No additional words and grammatical modifications are allowed. The more different words used in a sentence, the higher the score. The more detailed information in a sentence, the higher the score. The more different ways of saying it, the higher the score."
prompt_storytelling = "Your task is to write narratives using only the words from the Research Words List.\nThese are definitions of narrative.\n-Sharing personal experiences that should explain an event's who, what, why, when, where, and how while also being able to share some of your emotions.\n-Each narrative should be at least 5-6 sentences long.\n-Each narrative includes five elements: the setting, problem, emotion, action, and ending for example, \"I was playing cards with my brother(setting). My brother won the game(problem) and I got mad(emotion). So I asked him, \"Can you play again?\"(action) This time I won and I was happy. (ending)\"\n-The narratives should be on different topics, such as school, weekends, or something that irritated me.\nCan you write 3 narratives like talking to your friends? Follow these rules to write narratives.\n[rule]\n-ONLY use words from the research word list.\n-Avoid grammatical modifications like verb endings (-ed, -ing) and use the word as it appears in the list. It does not matter if the sentences are not grammatically correct. For example, you can not change the \"give\" to \"gives\" or \"gave\", even if it is grammatically correct.\n-The word list has phrases such as \"I'm hungry\" or \"I can't find what I want to say\". Use phrases directly from the list without changing form or splitting phrases.\n-The sentences don't have to be grammatically correct if you can't generate correct sentences with the words on the list. For example, if the list contains only {'dad', 'play', 'soccer', 'yesterday', 'park'}, \"Dad play soccer park yesterday\" is good to show \"my dad played soccer at a park yesterday\".\n-The more different words used in a sentence, the higher the score.\n-The more different ways of saying it, the higher the score. For example, \"I want you to open the window\" and \"Please open the window\" mean the same thing but are said in different ways."

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

def GPT(symbol_list, past_out = None):
    #history to build the model
    model_history = [
    {"role": "system", "content": [{"text": system_description,"type": "text"}]},
    {"role": "user","content": [{"text": prompt_storytelling,"type": "text"}]},
    {"role": "user","content": [{"text": f'[research word list] \n {symbol_list}',"type": "text"}]},
    {"role": "assistant","content": [{"text": "1. I was at school with my friends. I can't find my communication aid, and I feel frustrated. So I ask Educational staff for help. They find it, and I feel happy again.\n2. During the weekend, I go to the beach with my friends. I drop my bag in the water, and I'm really sad. My friends help me dry it off. We continue to have fun, and I feel better.\n3. Yesterday, I go to the supermarket with Mum. I can't find what I want to buy, and I'm feeling confused. I ask for help from Support staff. They help me find it, and I feel okay.","type": "text"}]},
    {"role": "user","content": [{"text": "[\"can't\", 'frustrated', 'for', 'during', 'drop', 'continue', 'better', 'okay'] are not on the list. Don't use these words.","type": "text"}]},
    {"role": "assistant","content": [{"text": "1. I was at school with my friends. I can not find my communication aid, and I feel bad. So I ask Educational staff help. They find it, and I feel happy again.\n2. On the weekend, I go to the beach with my friends. My bag is in the water, and I'm really sad. My friends help me dry it off. We have fun again.\n3. Yesterday, I go to the supermarket with Mum. I can not find what I want to buy, and I'm feeling confused. I ask help from Support staff. They help me find it, and I feel good.","type": "text"}]},
    {"role": "user","content": [{"text": "Generate another 5 narratives.","type": "text"}]},
    {"role": "assistant","content": [{"text": "4. Yesterday, at home with my sister. I say, \"I'm hungry,\" she make a meal with chicken nuggets and chips. I feel good eating in the dining room. She says, \"What do you think?\" I say, \"I like it,\" she laughs. \n5. My friends and I go to the supermarket on the weekend. I lose my money, I ask people, \"Have you seen my money?\" They help me look and we find it. I buy fruit and drink.  I'm feeling happy. \n6. Today, in my room, I want to chill out on my bed. My pet cat comes and sits with me. I feel relaxed. I say to my cat, \"I love you!\" It’s quiet and nice.\n7. At school, we have to do a work with my school/college/work mates. The problem was I leave my book at home, and I feel scared. I ask Educational staff to call Mum. Mum bring it, and I do well on the work, feeling relieved.\n8. In school yesterday, we have a special day. We play football. I feel tired and happy. Later, we have lunch with Educational staff. It’s a good day.","type": "text"}]},
    ]
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
    ahead = input("Do you want to use GPT? (Y/N) >>>")
    if ahead != "Y":
        print("stop generate")
        return None
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages= model_history + next_prompt,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )
    return(response.choices[0].message)

def generate_sentences(symbol_list):
    now = datetime.datetime.now()
    filename = 'experimet\communikate20' + '\generate_'+ now.strftime('%m%d%Y_%H%M%S') + '.txt'
    with open(filename, 'w', encoding="utf-8") as f:
        output = GPT(symbol_list)
        output = output.content.replace("\n\n", "\n")
        f.write(output)
        f.flush()
        os.fsync(f.fileno())
        past_output = output + "\n"
        for n in range(10):
            print(f'{n+1} times generation')
            if not output:
                break
            output = GPT(symbol_list,past_output)
            output = output.content.replace("\n\n", "\n")
            past_output = output + "\n"
            print(output)
            f.write(output)
            f.flush()
            os.fsync(f.fileno())
    return past_output

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
    symbol_list = interleave_dict_values("symbol_list\picomdata\comunicate_20\symbol_list.pkl")
    generate_sentences(symbol_list)