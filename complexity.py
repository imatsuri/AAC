from readability import Readability
from tqdm import tqdm
import pandas as pd
from matplotlib import pyplot as plt
import glob

#calculating the syntactic complexity input[sentences] -> output[#sentences, grade level]
def calculate_grade(texts):
    min_size = 100
    result = []
    num_sent = len(texts)
    input_text = ""
    
    for n, sentence in tqdm(enumerate(texts), total=num_sent):
        input_text += sentence.replace("\n", " ").replace(";", ".")
        if input_text[-2] != ". ":
            input_text = input_text.rstrip(" ") + ". "
        if min_size > 0:
            min_size -= len(sentence.split())
            continue
        else:
            r = Readability(input_text)
            estimated_grade = r.flesch_kincaid().score
            result.append([n+1, estimated_grade])
    return result

def calculate_ease(texts):
    min_size = 100
    result = []
    num_sent = len(texts)
    input_text = ""
    
    for n, sentence in tqdm(enumerate(texts), total=num_sent):
    #for n, sentence in enumerate(texts):
        input_text += sentence.replace("\n", " ").replace(";", ".")
        if input_text[-2] != ". ":
            input_text = input_text.rstrip(" ") + ". "
        if min_size > 0:
            min_size -= len(sentence.split())
            continue
        else:
            r = Readability(input_text)
            reading_ease = r.flesch().score
            result.append([n+1, reading_ease])
            #print(reading_ease, input_text)
    return result

#input from text file and save the result of complexity to pkl file
def from_txt(filename, outfile):
    with open(filename,"r", encoding="utf-8") as f:
        texts = f.readlines()
    #result = calculate(texts)
    result = calculate_grade(texts)
    #print(result)
    df = pd.DataFrame(result, columns =['num', 'score'])
    df.to_pickle(outfile)

def draw_graph(pkl, title):
    # フォントの種類とサイズを設定する。
    plt.rcParams['font.size'] = 15
    plt.rcParams['font.family'] = 'Arial' 
    
    fig, ax = plt.subplots()
    x = pkl["num"].squeeze().tolist()
    y = pkl["score"].squeeze().tolist()
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel("number of sentences", labelpad=15)
    ax.set_ylabel("grade level", labelpad=15)
    ax.set_ylim([0, 6])

    plt.show()

def plot_fourlines(pkls, title="Combined Graph", save_path=None):
    """pklsを受け取って1つの座標に4つの線を表示する関数"""
    color = ["b", "g", "r", "m", "orange"]
    labels = ["request_original", "request_separated", "story_original", "story_separated"]
    plt.figure(figsize=(10, 6))
    
    for i, (label, pkl) in enumerate(pkls):
        x = pkl["num"].squeeze().tolist()
        y = pkl["score"].squeeze().tolist()
        plt.plot(x, y, c=color[i], label=label)
    
    # グラフのタイトルとラベル
    plt.title(title)
    plt.xlabel('Number of sentences')
    plt.ylabel('Estimated grade level')
    #plt.ylim([0, 100])
    plt.legend()
    plt.grid(True)
    
    # 保存または表示
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

def from_pickle(filenames):
    if type(filenames) == str: #allow filenames to be a list OR a target folder name/glob search
        if "*" not in filenames and filenames[-1] != "/": #if users forgot to include the "/"
            filenames = filenames + "/*.pkl"    
        if filenames[-1] == "/":
            filenames = filenames + "*.pkl"
        filelist = glob.glob(filenames)
    elif type(filenames) == list:
        filelist = filenames

    pkls = []
    for filename in filelist:
        small_title = filename.split("\\")[-2]
        pkl = pd.read_pickle(filename)
        pkls.append([small_title, pkl])
    #pdb.set_trace()

    big_title = "Differences of grade level between datasets"
    #four_graph(pkls, big_title, big_title + "_4graph.png")
    plot_fourlines(pkls, big_title, save_path = big_title + "_4line.png")


from_txt("result\core112\\100samples.txt", "Input\core112\complexity.pkl")
pkl = pd.read_pickle('Input\core112\complexity.pkl')
draw_graph(pkl, "reading ease of storytelling")

from_pickle(['Input\communikate20\complexity.pkl', 'Input\quicksay_20\complexity.pkl', 'Input\ck20\complexity.pkl', 'Input\core60\complexity.pkl', 'Input\core112\complexity.pkl'])