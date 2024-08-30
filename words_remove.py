import re
from openai import OpenAI
import pickle as pl
import pdb
import datetime
import os

def check_words_in_list(word_list, text_list):
    # 単語リストをセットとリストに分ける
    single_words = set()
    phrases = []
    result = {}
    
    for item in word_list:
        item = item.strip()
        if ' ' in item and item != ' ':
            phrases.append(item.rstrip().lower())
        else:
            single_words.add(item.rstrip().lower())
    phrases.sort(key=len, reverse=True)
    #print(phrases)

    punctuation = r"[.,\'\"?!;:]"
    for n, sentence in enumerate(text_list):
        #print(f"{n+1}. {sentence.rstrip()}")
        result[n] = []
        sentence = sentence.replace("“", "\"").replace("”", "\"").replace("’", "\'").rstrip().lower()
        # フレーズの検証
        for phrase in phrases:
            if phrase in sentence:
                # フレーズが見つかった場合、そのフレーズを除去
                pattern = re.escape(phrase) + r'(?=\s|' + punctuation + r'|$)'
                sentence = re.sub(pattern, '', sentence).strip()
        
        # 残った文章を単語に分割
        words = sentence.rstrip().split()
        # 単語の検証
        for word in words:
            word = word.strip(".,?!\'\";:")
            if word == "":
                continue
            if word.lower() not in single_words:
                #print(f"    '{word}' is not on the symbol list")
                result[n].append(word)
        if result[n] != []:
            result[n] = list(set(result[n]))
            #print(f"    {result[n]} are not on the symbol list")
    return result

def load_symbols(pklfile):
    symbol_list = []
    with open(pklfile, 'rb') as f:
        category = pl.load(f)
    symbol_list += [item.strip() for sublist in category.values() for item in sublist if item.strip() not in symbol_list]
    return symbol_list

def Gpt(symbol_list, Input, freq=None):
    ##Description to process of removing words which are not on the list.
    system_description = "You will be provided with the \"Research Words List\". Given a sentence with incorrect words, replace these words with the word from the Research Words List.  Steps to follow: \n1. If the Research Words List contains different modifications for certain words (e.g. verb or noun endings), replace the incorrect words with the modified word. For example, if the list includes 'play', 'see', 'friend' but not 'played', 'saw', 'friends', replace them accordingly. \n2. Change the abbreviation to its normal form if you can express it with words in the list, as in \"can't\" and 'can not'.\n3. If the Research Words List includes a synonym for an incorrect word, replace the incorrect word with the synonym. For example, if the list includes 'Mum' but not 'mother' or 'look' but not 'watch', 'replace 'mother' with 'Mum' and 'watch' with 'look'. \n4. If the Research Words List includes a word of the same category as the incorrect word (i.e. a word that does not significantly change the intent of the sentence), replace the incorrect word with the word from the list. For example, if the list includes 'field' but not 'park', replace 'park' with 'field'. \n5. If none of the above steps are possible, respond with: \"It's impossible to replace [incorrect word]\".  Please note you don't have to maintain the original meaning and grammatical correctness of sentences.  \n**Example Input:**  \n1. At the park, I saw people. I was afraid. I said, \"I need some help.\" A friend came. We played sports. It was fun.  \n\t{'park', 'saw', 'said', 'friend', 'came', 'played'} are not on the list.\n The output format is “{sentence number}. {modified sentence}.” For example, \n1. At the field, I see people. I was afraid. I say, \"I need some help.\" Friends came. We play sports. It was fun. \n2. It's impossible to replace [incorrect word]"
    ## two Conversation history to call the model
    ## -message_normal: Input sentences and words 1. I want an apple ["an"] are not on the list
    ## -message_wordlim: prompt to prevent replace the same word over andd over. message_normal + Don't use these words [freq] 
    message_normal = [
      {
        "role": "system",
        "content": [
          {
            "text": system_description,
            "type": "text"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "text": f'[research word list] \n{symbol_list}',
            "type": "text"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "text": "1. I was at school with my friends. I can't find my communication aid, and I feel frustrated. So I ask Educational staff for help. They find it, and I feel happy again.\n    [\"can't\", 'frustrated', 'for'] are not on the symbol list\n3. Yesterday, I go to the supermarket with Mum. I can't find what I want to buy, and I'm feeling confused. I ask for help from Support staff. They help me find it, and I feel okay.\n    [\"can't\", 'for', 'okay'] are not on the symbol list\n4. I was at home when Dad asked for help in the garden. But I can't find the gardening tools, and I feel frustrated. So I ask Dad for help. He shows me where the tools are, and we start gardening together, and I feel happy.\n    ['asked', 'for', \"can't\", 'frustrated', 'for', 'shows', 'start', 'together'] are not on the symbol list\n5. At school, we had to do a project with my school mates. The problem was I left my notes at home, and I felt scared. I ask the teacher if I could call Mum. Mum brings the notes, and I do well on the project, feeling relieved.\n    ['had', 'project', 'mates', 'left', 'notes', 'felt', 'teacher', 'if', 'call', 'brings', 'notes', 'project', 'relieved'] are not on the symbol list",
            "type": "text"
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "text": "1. I was at school college with my friends. I can not find my communication aid, and I feel afraid. So I ask Educational staff some help. They find it, and I feel happy again.\n3. Yesterday, I go to the supermarket with Mum. I can not find what I want to buy, and I am feeling confused. I ask some help from Support staff. They help me find it, and I feel here.\n4. I was at home when Dad ask some help in the garden. But I can not find the gardening tools, and I feel afraid. So I ask Dad some help. He show me where the tools are, and we go gardening, and I feel happy.\n5. At school college, we do a timetable with my school college. The problem was I go my book at home, and I feel afraid. I ask the educational staff can I could Mum. Mum brings the book, and I do well on the timetable.\n",
            "type": "text"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "4. I was at home when Dad ask some help in the garden. But I can not find the gardening tools, and I feel afraid. So I ask Dad some help. He show me where the tools are, and we go gardening, and I feel happy.\n    ['show'] are not on the symbol list\n15. At school college, we do a timetable with my school college. The problem was I go my book at home, and I feel afraid. I ask the educational staff can I could Mum. Mum brings the book, and I do well on the timetable.\n    ['bring'] are not on the symbol list"
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": "10. I was at home when Dad ask some help in the garden. But I can not find the gardening tools, and I feel afraid. So I ask Dad some help. He put me where the tools are, and we go gardening, and I feel happy.\n11. At school college, we do a timetable with my school college. The problem was I go my that at home, and I feel afraid. I ask the Educational staff can I could Mum. Mum put the that, and I do well on the timetable, feeling."
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": Input
          }
        ]
      }
    ]
    message_wordlim = [
      {
        "role": "system",
        "content": [
          {
            "text": system_description,
            "type": "text"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "text": f'[research word list] \n {symbol_list}',
            "type": "text"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "text": "1. I was at school with my friends. I can't find my communication aid, and I feel frustrated. So I ask Educational staff for help. They find it, and I feel happy again.\n    [\"can't\", 'frustrated', 'for'] are not on the symbol list\n3. Yesterday, I go to the supermarket with Mum. I can't find what I want to buy, and I'm feeling confused. I ask for help from Support staff. They help me find it, and I feel okay.\n    [\"can't\", 'for', 'okay'] are not on the symbol list\n4. I was at home when Dad asked for help in the garden. But I can't find the gardening tools, and I feel frustrated. So I ask Dad for help. He shows me where the tools are, and we start gardening together, and I feel happy.\n    ['asked', 'for', \"can't\", 'frustrated', 'for', 'shows', 'start', 'together'] are not on the symbol list\n5. At school, we had to do a project with my school mates. The problem was I left my notes at home, and I felt scared. I ask the teacher if I could call Mum. Mum brings the notes, and I do well on the project, feeling relieved.\n    ['had', 'project', 'mates', 'left', 'notes', 'felt', 'teacher', 'if', 'call', 'brings', 'notes', 'project', 'relieved'] are not on the symbol list",
            "type": "text"
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "text": "1. I was at school college with my friends. I can not find my communication aid, and I feel afraid. So I ask Educational staff some help. They find it, and I feel happy again.\n3. Yesterday, I go to the supermarket with Mum. I can not find what I want to buy, and I am feeling confused. I ask some help from Support staff. They help me find it, and I feel here.\n4. I was at home when Dad ask some help in the garden. But I can not find the gardening tools, and I feel afraid. So I ask Dad some help. He show me where the tools are, and we go gardening, and I feel happy.\n5. At school college, we do a timetable with my school college. The problem was I go my book at home, and I feel afraid. I ask the educational staff can I could Mum. Mum brings the book, and I do well on the timetable.\n",
            "type": "text"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "4. I was at home when Dad ask some help in the garden. But I can not find the gardening tools, and I feel afraid. So I ask Dad some help. He show me where the tools are, and we go gardening, and I feel happy.\n    ['show'] are not on the symbol list\n15. At school college, we do a timetable with my school college. The problem was I go my book at home, and I feel afraid. I ask the educational staff can I could Mum. Mum brings the book, and I do well on the timetable.\n    ['bring'] are not on the symbol list"
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": "10. I was at home when Dad ask some help in the garden. But I can not find the gardening tools, and I feel afraid. So I ask Dad some help. He put me where the tools are, and we go gardening, and I feel happy.\n11. At school college, we do a timetable with my school college. The problem was I go my that at home, and I feel afraid. I ask the Educational staff can I could Mum. Mum put the that, and I do well on the timetable, feeling."
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": f'Don\'t use {freq}'
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": Input
          }
        ]
      }
    ]

    ## Build the ChatApi model
    if freq:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=message_wordlim,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "text"
            }
        )
    else:
        client = OpenAI()
        response = client.chat.completions.create(
              model="gpt-4o",
              messages=message_normal,
              temperature=1,
              max_tokens=1024,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0,
              response_format={
                  "type": "text"
              }
        )
    return response.choices[0].message

def replace_words(symbol_list, Output, folder):
    now = datetime.datetime.now()
    log_file = "log/" + folder.split("/")[-1] + '/remove_'+ now.strftime('%m%d%Y_%H%M%S') + '.txt'
    okay = []
    include = []
    freq = []
    #replace words by GPT
    pattern = r'^\d+\.\s'
    texts = [line[3:] for line in Output.split("\n") if re.match(pattern, line) and "It's impossible to replace [" not in line]
    result = check_words_in_list(symbol_list, texts)
    with open(log_file, 'w', encoding="utf-8") as f:
        f.write(Output)
        f.flush()
        os.fsync(f.fileno())
        for n in range(4):
            #pdb.set_trace()
            f.write("\n-----------------------------------------------------------------------\n")
            f.write(f"try {n}\n")
            Input = ""
            for sample_num, sample in enumerate(texts):
                #pdb.set_trace()
                if result[sample_num] == []:
                    okay.append(sample)
                    f.write(f'{sample_num} is okay\n')
                elif "It's impossible to replace [" in sample:
                    continue
                else:
                    include.append(sample)
                    Input += f'{sample_num}. {sample.rstrip()}\n   {result[sample_num]} are not on the list \n'
            if Input == "":
                print("all words are on the list")
                texts = []
                break
            f.write(f"Next Input:\n{Input}")
            f.write(f"Don't use: {freq}\n")
            f.flush()
            os.fsync(f.fileno())
            """
            ahead = input("Do you want to use GPT? (Y/N) >>>")
            if ahead != "Y":
                print("stop the fixing")
                break
            """
            #call GPT model
            Output = Gpt(symbol_list, Input, freq)
            print(Output.content)
            f.write(f'output: \n{Output.content}\n')
            f.flush()
            os.fsync(f.fileno())
            texts = [line[3:] for line in Output.content.split("\n") if re.match(pattern, line) and "It's impossible to replace [" not in line]
            result = check_words_in_list(symbol_list, texts)
            freq += [item for sublist in result.values() for item in sublist if item not in freq]
    dataset = delete_words(texts, okay.copy(), result, freq)
    return okay + texts, dataset

def delete_words(texts, dataset, result, freq):
    #remove the sentences which contain words can't be replaced
    for sample_num, sample in enumerate(texts):
        if result[sample_num] == []:
            dataset += [sample]
            print(f'{sample_num} is okay')
        else:
            after_remove = ""
            pattern = re.compile(r'(?<!\.\.\.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s')
            sentences = pattern.split(sample.rstrip())
            # 文章を分割
            for sentence in sentences:
                flg = False
                sent_split = sentence.lower().split()
                for word in sent_split:
                    word = word.strip(".,?!\'\"")
                    if word.lower() in freq:
                        flg = True
                        break
                if flg:
                    continue
                after_remove = after_remove + sentence + " "
            dataset.append(after_remove.rstrip())
    return dataset

def remove_by_GPT(folder, Output):
    symbol_list = load_symbols(folder + "/symbol_list.pkl")
    gpt_generate, dataset = replace_words(symbol_list, Output, folder)
    return gpt_generate, dataset

if __name__ == "__main__":
    folder = "Input/quicksay_20"
    Output = "1. Yesterday, sister and I played basketball in the gymnasium. She kept scoring points, and I couldn't catch up. I felt really bad and frustrated. I told her, \"I need more practice to get better.\" She smiled and said, \"We can practice together.\" I felt hopeful and ready to improve.\n2. This morning, brother and I ate breakfast at kitchen table. The food was delicious, but something strange happened. I found toy inside my cereal box! I felt surprised and called out, \"Mom, look at this!\" Mom laughed and said it must have been a mistake from the store.\n3. Sunday afternoon, I'm outside with friends playing soccer by the park. Suddenly, it started raining heavily. We were all wet and dirty; everyone was annoyed. One friend suggested going inside his house instead. We ended up playing video games and had fun indoors.\n4. Last week in art class, teacher asked us to draw pictures of our favorite things. I drew a picture of my dog because he makes me feel joyful every day. When showing my drawing to classmates, they all liked it very much! I felt so proud of myself for doing good job.\n5. During movie night with family in living room last night, we watched funny film together on TV screen. It made us all laugh so hard! After movie ended, dad made hot chocolate for everyone while mom brought cookies from kitchen cupboard. The evening was perfect; everyone went to bed happy."
    fix_data, dataset = remove_by_GPT(folder, Output)
    print(fix_data)
    print(dataset)