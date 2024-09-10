import pickle as pl
import glob
import re
import pdb
from coverage import count_symbols, extract_categry

def same_symbols_rate(file1, file2):
    with open(file1, "rb") as f:
        category = pl.load(f)
        data1 = [symbol for values in category.values() for symbol in values]
    with open(file2, "rb") as f:
        category = pl.load(f)
        data2 = [symbol for values in category.values() for symbol in values]
    
    #data1 = [re.sub(r'([a-z])([A-Z])', r'\1 \2', s).lower() for s in data1]
    data1 = [s.replace("’", "'").strip("\'\"' '").lower() for s in data1]
    data2 = [s.replace("’", "'").strip("\'\"' '").lower() for s in data2]

    l1_l2 = set(data1) & set(data2)
    print(f'data1: {len(set(data1))} symbols,  data2: {len(set(data2))} symbols')
    #print(set(data1) - l1_l2)
    print(f"{len(l1_l2)} words are same")
    print(f'same words rate for data1:  {len(l1_l2)/len(set(data1))}')
    print(f'                for data2:  {len(l1_l2)/len(set(data2))}')
    #print(f'{l1_l2}\n')

    return l1_l2
    """
    used_l1l2 = set(used) & l1_l2
    print(f'same words rate:  {len(l1_l2)/len(set(data2))}')
    print(f'in datasets rate: {len(used_l1l2)/len(used)}')
    """

def used_symbols_rate(symbol1, symbol2, dataset1, dataset2):
    same = same_symbols_rate(symbol1, symbol2)
    print(f"---------{symbol1}--------")
    category = extract_categry(symbol1)
    a, used_1 = count_symbols(dataset1, category)
    samerate_1 = same & set(used_1)
    print(f"{len(samerate_1)} words are not unique")
    print(f"same words rate: {len(samerate_1) / len(set(used_1))}")
    print(f"---------{symbol2}--------")
    category = extract_categry(symbol2)
    a, used_2 = count_symbols(dataset2, category)
    samerate_2 = same & set(used_2)
    print(f"{len(samerate_2)} words are not unique")
    print(f"same words rate: {len(samerate_2) / len(set(used_2))}")

    l1_l2 = set(used_1) & set(used_2)
    print(f"---------same words--------")
    print(f"{len(l1_l2)} words are same")
    print(f"same words rate: {len(l1_l2) / len(set(used_2))}")


"""
with open("symbol_list\picomdata\comunicate_20\symbol_list2.pkl", "rb") as f:
    category = pl.load(f)
    communi_20 = [symbol for values in category.values() for symbol in values]
a, used = count_symbols("com.txt", communi_20)

folder = "symbol_list\picomdata/picomdata/*.txt"
filenames = glob.glob(folder)
filenames += ["symbol_list\\astegrid\Global-Core_Communicator_ARASAAC\\aste_symbols_2.txt", "symbol_list\\astegrid\quick_20\quick.txt"]

filenames = ["symbol_list\cboard\cboad_symbols.txt"]
for filename in filenames:
    print(f'------------------{filename}-------------------')
    com2(filename, communi_20, used)
"""

if __name__ == "__main__":
    used_symbols_rate("Input\core112\symbol_list.pkl", "Input\quicksay20\symbol_list.pkl","result\core112\\100samples.txt", "result\quicksay20\\100samples.txt")
