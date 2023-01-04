'''
使用各种构造错误的方法生成错误句子的流程。
'''
from .confusion import PinyinCharConfusion, PinyinWordConfusion, StrokeCharConfusion
from .hmm import HMM
from .pinyinapi import PinyinInputApi
from .add_delete_char import CharAddDelete
from  LAC import LAC
import pycorrector as pc 
from cache import LruCache
import random 
random.seed(33)

class GenErrorText:
    def __init__(self) -> None:
        self.pinyinchar_confusion = PinyinCharConfusion()
        self.pinyinword_confusion = PinyinWordConfusion()
        self.strokechar_confusion = StrokeCharConfusion()
        self.pinyinapi = PinyinInputApi()
        self.charadddelete = CharAddDelete()
        self.hmm = HMM()
        self.lac = LAC()
        self.choices = [ 
            self.pinyinchar_confusion, 
            self.pinyinchar_confusion,
            self.pinyinchar_confusion,  #拼音替换占30%
            self.hmm,                   #隐马全拼替换占20%
            self.strokechar_confusion,  #字形替换占10%
            self.pinyinword_confusion,  #同音词替换占10%
            self.charadddelete,         #添加删除交换占10%
            self.pinyinapi,             #拼音api替换占20%
            self.pinyinapi

        ]

    

    @LruCache(maxsize=200, timeout=100)
    def forbidden_pos(self, text):
        '''
        找出不能造错的位置。目前确定的是非中文字符、人名PER、地名LOC、组织名ORG、时间TIME、作品名nw
        '''
        res = []
        
        if not text:
            return res 
        #所有非中文的字符不能作为造错候选
        for i, c in enumerate(text):
            if not pc.text_utils.is_chinese(c):
                res.append(i)

        text, pos  = self.lac.run(text)
        cur = 0
        for w , p in zip(text, pos):
            if p in ("PER", "LOC", "ORG", "TIME", "nw"):
                for i in range(len(w)):
                    res.append(cur+i)
            cur += len(w)

    
    def select_pos(self, text):
        poses = list(range(len(text)))
        forbidden = self.forbidden_pos(text)
        poses = list(set(poses)-set(forbidden))
        select = random.choice(poses)
        return select  

    def select_noiser(self):
        return random.choice(self.choices)


    def seg_text(self, text, stride=15):
        words, _ = self.lac.run(text)
        res = []
        cur_index = 0
        while cur_index < len(words):
            res.append("".join(words[cur_index: cur_index+stride]))
            cur_index += stride
            

    def generate_block(self, block):
        pos = self.select_pos(block)
        noiser = self.select_noiser()
        res = noiser.error_text(block, pos=pos)
        return res 
        


    def generate(self, text):
        blocks = self.seg_text(text)
        res = []
        for block in blocks:
            err = self.generate_block(block)
            res.append(err)
        return "".join(res)

        


if __name__ == "__main__":
    tests = [
        ""
    ]







    