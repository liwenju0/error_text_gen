import random
import jieba
from pypinyin import pinyin, lazy_pinyin, Style
import requests
import time
import json
import os 

random.seed(1000)

class PinyinInputApi:
    def __init__(self) -> None:
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")
        self.confusion = self.read_confusion(os.path.join(self.base_path, "confusion_letters.txt"))
        self.baiduapi = "http://olime.baidu.com/py?input={}&inputtype=py&bg=0&ed=20&result=hanzi&resultcoding=unicode&ch_en=0&clientinfo=web&version=1"
        self.googleapi = "https://inputtools.google.com/request?text={}&itc=zh-t-i0-pinyin&num=6&cp=0&cs=1&ie=utf-8&oe=utf-8&app=demopage"
    def read_confusion(self, file_path):
        """ Read Pinyin confusion set
        """
        with open(file_path, "r", encoding="utf-8") as confile:
            confusion = {}
            for line in confile:
                letter, confs = line.strip("\n").split(":")
                confusion[letter] = confs
        return confusion

    def error_text(self, text, pos=0, cand_num=5):
        res = []
        words = jieba.lcut(text)
        cur_index = 0
        pos_word=-1
        for i, w in enumerate(words):
            if cur_index <= pos <= cur_index+len(w):
                pos_word = i
                break 
            cur_index += len(w)
        if pos_word == -1:
            return res 

        word = words[pos_word]
        res = []
        cnt = 0
        used = []
        while cnt < 2*len(self.orig_pinyin(word)) and len(res) != cand_num:
            cnt += 1
            cand_word = self.do_replace(word, "mix")
            
            if cand_word != word and cand_word not in used:
                used.append(cand_word)
                res.append("".join(words[:pos_word]+[cand_word] + words[pos_word+1:]))
        return res 

    def orig_pinyin(self, word):
        """ Get original Pinyin
        """
        _pinyin = lazy_pinyin(word)
        _pinyin = ''.join(_pinyin)
        return _pinyin


    def abbrv_pinyin(self, word):
        """ Get Pinyin with only taking the first letter if it's the last word
        """
        _first = pinyin(word, style=Style.FIRST_LETTER)
        _pinyin = lazy_pinyin(word)
        _pinyin[-1] = _first[-1][0]
        _pinyin = ''.join(_pinyin)
        return _pinyin


    def cut_pinyin(self, word):
        """ Get Pinyin missing some letter when the length of Pinyin greater than 1
        """
        _pinyin = lazy_pinyin(word)
        _pinyin = ''.join(_pinyin)
        if len(_pinyin) > 1:
            _pinyin = _pinyin.replace(random.choice(_pinyin), '', 1)
        return _pinyin


    def add_pinyin(self, word):
        """ Get Pinyin with redundant letters
        """
        _pinyin = lazy_pinyin(word)
        _pinyin = list(''.join(_pinyin))
        length = len(_pinyin)
        index = random.randint(0, length-1)
        letter = _pinyin[index]
        if letter in self.confusion.keys():
            rechar = random.choice(self.confusion[letter])
            _pinyin.insert(index, rechar)
        _pinyin = ''.join(_pinyin)
        return _pinyin


    def change_pinyin(self, word):
        """ Get Pinyin with some letter errors
        """
        _pinyin = lazy_pinyin(word)
        _pinyin = ''.join(_pinyin)
        letter = random.choice(_pinyin)
        if letter in self.confusion.keys():
            rechar = random.choice(self.confusion[letter])
            _pinyin = _pinyin.replace(letter, rechar, 1)
        return _pinyin


    def get_baidu_candidates(self, _pinyin):
        """ Get candidates of inputting method
        """
        url = self.baiduapi.format(_pinyin)        
        for i in range(10):
            try:
                result = requests.get(url)
            except:
                if i >= 9:
                    return [_pinyin]
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.1)
                break
        candidates = []
        # print(result.json())
        if result.json()['status'] == 'T':
            for cand in result.json()["result"][0]:
                candidates.append(cand[0])
        return candidates

    
    def get_google_candidates(self, _pinyin):
        """ Get candidates of inputting method
        """
        url = self.googleapi.format(_pinyin)
        
        for i in range(10):
            try:
                result = requests.get(url)
            except:
                if i >= 9:
                    return [_pinyin]
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.1)
                break
        candidates = []
        # print(result.json())
        if result.json()[0] == 'SUCCESS':
            candidates = result.json()[1][0][1]
        return candidates


    def orig_select(self, candidates):
        """ Randomly select from candidate words
        """
        candidate = random.choice(candidates)
        return candidate


    def strict_select(self, word, candidates):
        """ Randomly select from the candidates with the same length as the original word
        """
        length = len(word)
        strict_candidates = []
        for item in candidates:
            if len(item) == length:
                strict_candidates.append(item)
        if not strict_candidates:
            return word
        candidate = random.choice(strict_candidates)
        return candidate


    def loose_select(self, word, candidates):
        """ Randomly select from the candidates whose length differ from the original word by no more than 1
        """
        length = len(word)
        loose_candidates = []
        for item in candidates:
            if abs(len(item) - length) <= 1:
                loose_candidates.append(item)
        if not loose_candidates:
            return word
        candidate = random.choice(loose_candidates)
        return candidate


    def do_replace(self, word, strategy=''):
        """ Replace the original word
        """
        #必须是中文词语
        api = self.get_baidu_candidates
        for ch in word:
            if not '\u4e00' <= ch <= '\u9fa5' and not 'A' <= ch <= 'Z' and not 'a' <= ch <= 'z':
                return word

        if strategy == '':
            _pinyin = self.orig_pinyin(word)
            candidates = api(_pinyin)
            reword = self.strict_select(word, candidates)
        
        if strategy == 'mix':
            switcher = {
                1: self.abbrv_pinyin,
                2: self.cut_pinyin,
                3: self.add_pinyin,
                4: self.change_pinyin
            }
            fun = random.randint(1, 4)
            # print("function:", fun)
            function = switcher.get(fun)
            _pinyin = function(word)
            candidates = api(_pinyin)
            reword = self.loose_select(word, candidates)

        # print("Pinyin:", _pinyin)
        # print("candidates:", candidates)
        # print("reword:", reword)
        return reword


def gen_data(sentence, strategy, confusion):
    """ Generate an error correction data
    """
    # truncation = min(len(sentence), 256)  # 文本长度超过 256 进行截断
    # sentence = sentence[:truncation]

    words = list(jieba.cut(sentence))
    print("words:", words)
    length = len(words)
    count = random.randint(1,3)
    if count > length: count = 1
    index = random.sample(range(length), count)

    gen_text = ''
    for idx, word in enumerate(words):
        if idx in index:
            gen_text += do_replace(word, strategy, confusion)
        else:
            gen_text += word
    
    data = {
        "original_text": gen_text,
        "correct_text": sentence,
        "flag": gen_text == sentence
    }
    return data


def do_gen_data(sentences, num, strategy, confusion):
    """ Generate a specified amount of error correction datas
    """
    datas = []
    samples = random.sample(sentences, num)  # 随机选取 num 个句子进行替换
    for sample in samples:
        datas.append(gen_data(sample, strategy, confusion))
    return datas


def save_data(datas, save_path):
    """ Save datas
    """
    with open(save_path, "w", encoding="utf-8") as outfile:
        datas = json.dumps(datas, ensure_ascii=False, indent=2)
        outfile.write(datas)


if __name__ == '__main__':
    api = PinyinInputApi()
    print(api.error_text("真是非常的好吃", 3, 5))


