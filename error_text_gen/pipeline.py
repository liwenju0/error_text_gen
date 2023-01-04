'''
使用各种构造错误的方法生成错误句子的流程。
'''
from confusion import PinyinCharConfusion, PinyinWordConfusion, StrokeCharConfusion
from hmm import HMM
from pinyinapi import PinyinInputApi
from add_delete_char import CharAddDelete
from  LAC import LAC
import pycorrector as pc 
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
        self.lac = LAC(use_cuda=True)
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

        return res 

    
    def select_pos(self, text):
        poses = list(range(len(text)))
        forbidden = self.forbidden_pos(text)
        poses = list(set(poses)-set(forbidden))
        select = None
        if poses:
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

        return res 
            

    def generate_block(self, block):
        pos = self.select_pos(block)
        if not pos:
            return []
        noiser = self.select_noiser()
        res = noiser.error_text(block, pos=pos)
        return res

    def generate(self, text):
        blocks = self.seg_text(text)
        res = []
        for block in blocks:
            err = self.generate_block(block)
            if err:
                res.append(err[0])
            else:
                res.append(block)
        
        return "".join(res)

        
if __name__ == "__main__":
    tests = '''央广网重庆1月31日消息(记者吴新伟)重庆市纪委监察委官微"风正巴渝"今披露,该市近日通报3起违反中央八项规定精神问题。
            据通报,重庆长寿化工有限责任公司党委委员、董事、副总经理李文成违规发放津补贴。
            2013年4月至2017年11月,李文成违规以节日津补贴等名义向公司办公室职工发放11万余元,其中本人违规领取3.2万余元。
            2018年7月,李文成受到党内严重警告处分、扣减2017年全部绩效年薪处理；
            违纪款项已清退。
            垫江县原卫生和计划生育委员会党委书记、主任刘卫东违规收受礼金问题。
            2013年1月至2017年1月,刘卫东在任垫江县原卫生局党委书记、局长,以及垫江县原卫生和计划生育委员会党委书记、主任期间,先后收受管理服务对象礼金共计4万元；
            同时,刘卫东还存在其他严重违纪违法问题。
            2018年9月,刘卫东受到开除党籍、开除公职处分'''
    generator = GenErrorText()
    sents = [t.strip() for t in tests.split("\n")]
    sents = ['奥得河畔科斯琴18世纪以后由法国在1806年拍摄的，Küstrin占领了法国军事驻军的的剩余拿破仑战争。']
    for sent in sents:
        err = generator.generate(sent)  
        print(sent)
        print(err)








    