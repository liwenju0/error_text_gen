'''
使用提前收集好的，音近字、形近字、同音词、构造错误数据。
'''
import os 
import json
import pypinyin
import random 
from LAC import LAC
class PinyinCharConfusion:
    def __init__(self) -> None:
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")
        self.same_pinyin = {}
        for line in open(os.path.join(self.base_path, "same_pinyin.txt")):
            line = line.strip()
            line = line.split()
            self.same_pinyin[line[0]] = line[1:] if len(line) > 1 else []
        print("inited PinyinCharConfusion")

    
    def error_text(self, text, pos=0, cand_num=5):
        if pos >= len(text):
            return []
        char = pypinyin.lazy_pinyin(text[pos])[0]
        res = []
        if char in self.same_pinyin:
            rechars = self.same_pinyin[char]
            if not rechars:
                return res
            if cand_num >= len(rechars):
                for c in rechars:
                    res.append(text[:pos] + c + text[pos+1:])
                return res
            cnt = 0
            used = []
            while len(res) != cand_num and cnt < len(rechars)*2:
                cnt += 1
                c = rechars[random.randint(0, len(rechars)-1)]
                if c in used:
                    continue
                used.append(c)
                res.append(text[:pos] + c + text[pos+1:])
                
        return res 


class StrokeCharConfusion:
    def __init__(self) -> None:
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")
        self.same_stroke = {}
        for line in open(os.path.join(self.base_path, "same_stroke.txt")):
            line = line.strip()
            line = line.split()
            self.same_stroke[line[0]] = line[1:] if len(line) > 1 else []
        print("inited StrokeCharConfusion")
    
    def error_text(self, text, pos=0, cand_num=5):
        if pos >= len(text):
            return []
        char = text[pos]
        res = []
        if char in self.same_stroke:
            rechars = self.same_stroke[char]
            if not rechars:
                return res
            if cand_num >= len(rechars):
                for c in rechars:
                    res.append(text[:pos] + c + text[pos+1:])
                return res
            cnt = 0
            used = []
            while len(res) != cand_num and cnt < len(rechars)*2:
                cnt += 1
                c = rechars[random.randint(0, len(rechars)-1)]
                if c in used:
                    continue
                used.append(c)
                res.append(text[:pos] + c + text[pos+1:])
                
        return res 


class PinyinWordConfusion:
    def __init__(self) -> None:
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")
        self.same_pinyin_word = json.load(open(os.path.join(self.base_path, "same_pinyin_word.json")))
        self.lac = LAC()
        print("inited PinyinWordConfusion")
    
    def error_text(self, text, pos=0, cand_num=5):
        res = []
        words = self.lac.run(text)[0]
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
        py = "_".join(pypinyin.lazy_pinyin(word))
        if py in self.same_pinyin_word:
            rewords = [ w for w in self.same_pinyin_word[py] if w != word]
            if not rewords:
                return res
            if cand_num >= len(rewords):
                for c in rewords:
                    res.append("".join(words[:pos_word] + [c] + words[pos_word+1:]))
                return res
            cnt = 0
            used = []
            while len(res) != cand_num and cnt < len(rewords)*2:
                cnt += 1
                c = rewords[random.randint(0, len(rewords)-1)]
                if c in used:
                    continue
                used.append(c)
                res.append("".join(words[:pos_word] + [c] + words[pos_word+1:]))
                
        return res 



if __name__ == "__main__":
    pyconfusion = PinyinCharConfusion()
    wordconfusion = PinyinWordConfusion()
    strokeconfusion = StrokeCharConfusion()
    print(pyconfusion.error_text("我们一起来到这个地方",5, 5))
    print(wordconfusion.error_text("我们一起来到这个地方",5, 5))
    print(strokeconfusion.error_text("我们一起来到这个地方",5, 5))