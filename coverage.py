import pickle as pl
import re
import itertools
import pdb

def extract_categry(pklfile):
    with open(pklfile, 'rb') as f:
        category = pl.load(f)
    return category

def count_symbols(dataset, category, outfile = None):
    symbols = [symbol.strip() for value in category.values() for symbol in value]
    sym_dict = {symbol.lower():0 for symbol in symbols}
    phrases = []
    used = set()
    with open(dataset, "r", encoding="utf-8") as f:
        texts = f.readlines()
    #print(phrases)
    for item in symbols:
        item = item.strip()
        if ' ' in item and item != ' ':
            phrases.append(item.lower())
    phrases.sort(key=len, reverse=True)
    #print(phrases)

    punctuation = r"[.,\'\"?!;:]"
    for sentence in texts:
        sentence = sentence.replace("“", "\"").replace("”", "\"").replace("’", "\'").rstrip().lower()
        # フレーズの検証
        for phrase in phrases:
            if phrase in sentence:
                # フレーズが見つかった場合、そのフレーズを除去
                pattern = re.escape(phrase) + r'(?=\s|' + punctuation + r'|$)'
                sentence = re.sub(pattern, '', sentence).strip()
                if sym_dict[phrase] == 0:
                    used.add(phrase)
                sym_dict[phrase] += 1
        
        for word in sentence.strip().split(" "):
            word = word.strip(".,?!\'\";:")
            if word == "":
                continue
            if word.lower() in sym_dict.keys():
                if sym_dict[word.lower()] == 0:
                    used.add(word.lower())
                sym_dict[word.lower()] += 1
            else:
                print(word + " is not on the symbol list")
    print(f'word coverage: {len(used)/len(set(symbols))}')
    print(f'{len(used)} of {len(set(symbols))} are used')
    return sym_dict, used

def category_coverage(dataset, categories, outfile=None):
    sym_dict, a = count_symbols(dataset, categories)
    #pdb.set_trace()
    sym_analy = {}
    for category, symbol_list in categories.items():
        #pdb.set_trace()
        sym_analy[category] = {symbol: sym_dict[symbol.rstrip().lower()] for symbol in symbol_list}

    cov = dict()
    zero = []
    #all_sum = sum(sym_dict.values())
    for category, symbol_dict in sym_analy.items():
        counts = symbol_dict.values()
        if sum(counts) == 0:
            zero.append(category)
        all_kinds = len(counts)
        on_kinds = len([count for count in counts if count != 0])
        if all_kinds == 0:
            continue
        else:
            cov[category] = [on_kinds / all_kinds, on_kinds, all_kinds]
    print(f'category coverage: {1-(len(zero)/len(sym_analy.keys()))}')
    print(f'{len(sym_analy.keys())-len(zero)} of {len(sym_analy.keys())} are used')

    if outfile:
        with open(outfile, "w") as f:
            for key , data in cov.items():
                if isinstance(data, list):
                    f.write( key + "," + str(data[0])+ "," + str(data[1]) + "," + str(data[2]) + "\n")
                else:
                    f.write( key + "," + data + "\n")
            f.write(f'category coverage: {1-(len(zero)/len(sym_analy.keys()))}')

"""
def new_dataorder(sym_analy):
    category = dict()
    remove = []
    for cat_keys, cat_value in sym_analy.items():
        sorted_items = []
        for symbol, count in cat_value.items():
            if count == 0:
                sorted_items.append(symbol)
            else:
                remove.append(symbol)
        category[cat_keys] = sorted_items
    order = interleave_dict_values(category)
    order.extend(remove)
    return order
"""

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

def normal_order(count_result, lastorder):
    sorted_items = [key for key, value in count_result.items() if value > 0]
    order = [sym for sym in lastorder if sym.lower() not in sorted_items]
    order.extend(sorted_items)
    return order

def rotation(dataset_file, symbol_pkl):
    category = extract_categry(symbol_pkl)
    sym_dict, used = count_symbols(dataset_file, category)
    old_order = interleave_dict_values(symbol_pkl)
    print("------first order--------")
    print(old_order)
    new_order = [sym for sym in old_order if sym.lower() not in used]
    new_order.extend(used)
    print("------next order--------")
    print(new_order)

if __name__ == "__main__":
    board_name = "CK20"
    category = extract_categry("Input\\"+board_name+"\\symbol_list.pkl")
    category_coverage("result\\"+board_name+"\\100samples.txt", category, "result\\"+board_name+"\\category.txt")
    #category_coverage("result\\"+board_name+"\\50samples.txt", category)
    #rotation("result\quick20.txt", "Input\quicksay_20\symbol_list.pkl")