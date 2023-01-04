'''
调用训练好的HMM拼音输入法，获得错误数据。仅支持全拼。
'''
import os 
import numpy as np
import pypinyin

class Netnode(object):
    def __init__(self, word, count, phrase):
        self.word = word
        self.maxscore = 0.0
        self.prevN = None
        self.count = count
        self.phrase = phrase

class Longest(object):
    def __init_(self):
        self.prob = 0.0
        self.order = 0
        self.prev = None
        self.next = None

class Wordnet(object):
    def __init__(self, spells, table, wordmapping, wordnum, wordmatrix):
        self.orders = []
        #print(spells)
        for py in spells:
            #print(py)
            order = []
            wordlist = table[py]
            #print(wordlist)
            for word in wordlist:
                id = wordmapping[word]
                count = wordnum[id]
                phrase = wordmatrix[id][:]
                node = Netnode(word, count, phrase)
                order.append(node)
            self.orders.append(order)


class HMM:
    def __init__(self) -> None:
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data/hmm_model")
        self.table = np.load(os.path.join(self.base_path, "table.npy"), allow_pickle=True).item()
        self.wordmapping = np.load(os.path.join(self.base_path,'mapping.npy'), allow_pickle=True).item()
        self.wordmatrix = self._wordmatrix(os.path.join(self.base_path, "simple_matrix.txt"))
        self.wordnum = np.load(os.path.join(self.base_path, 'num.npy'), allow_pickle=True)
        self.totalcount = sum(self.wordnum)

    def _wordmatrix(self, path):
        wordmatrix = np.zeros([6763, 6763])
        matrix = open(path, 'r')
        for line in matrix:
            row = line.split()
            row_num = int(row[0])
            for i in range(int((len(row)-2)/2)):
                wordmatrix[row_num][int(row[2*i+1])]=int(row[2*i+2])
        matrix.close()
        return wordmatrix

    def error_text(self, text:str, pos=0, cand_num=1):
        '''
        返回text pos 位置的字符的易错字符集，默认返回5个。
        '''
        res = []
        cut_text = text[:pos+1]
        try:
            spells = pypinyin.lazy_pinyin(cut_text)
            new_pys = []
            for py in spells:
                if py == 'qv':
                    new_pys.append('qu')
                elif py == 'xv':
                    new_pys.append('xu')
                else:
                    new_pys.append(py)
            mywordnet = Wordnet(new_pys, self.table, self.wordmapping, self.wordnum, self.wordmatrix)
            #print(new_pys)
            self._hmm(mywordnet)
            
            cands = self.gen_error_char(mywordnet, cut_text[-1])
            # print('input:%s\n：%soutput\n' % (text, res[:5]))
            for c in cands[:cand_num]:
                res.append(text[:pos]+c+text[pos+1:])
            return res 
        except Exception as e:
            return res 

    def _hmm(self, wordnet: Wordnet):
        def hmm_i(i, wordnet):
            if i == 0: # the first spell
                for nodej in wordnet.orders[i]:
                    idj = self.wordmapping[nodej.word]
                    numj = self.wordnum[idj]
                    nodej.maxscore = numj / self.totalcount
                return
            for nodej in wordnet.orders[i]:
                probs =  []
                idj = self.wordmapping[nodej.word]
                for nodek in wordnet.orders[i-1]:
                    idk = self.wordmapping[nodek.word]
                    numk = self.wordnum[idk]
                    if numk == 0:
                        Emit = 0
                    else:
                        Emit = nodek.phrase[idj] / numk
                    probs.append(nodek.maxscore * Emit)
                # Get the maximum probability at the i-1 spell
                maxk = probs.index(max(probs))
                nodej.maxscore = probs[maxk]
                nodej.prevN = wordnet.orders[i-1][maxk]
            return
        order_len = len(wordnet.orders)
        for i in range(order_len):
            hmm_i(i, wordnet)

    def gen_error_char(self, wordnet, target):
        maxscore = []
        order_len = len(wordnet.orders)

        for node in wordnet.orders[order_len-1]:
            maxscore.append(node.maxscore)
        def argsort(seq):
            return sorted(range(len(seq)), key=seq.__getitem__, reverse=True)
        sorted_node = argsort(maxscore)
        res = []
        for nodeidx in sorted_node:
            if wordnet.orders[order_len-1][nodeidx].word != target:
                res.append(wordnet.orders[order_len-1][nodeidx].word)
        return res

if __name__ == "__main__":
    hmm = HMM()
    print(hmm.error_text("我们一起来到这个地方",5, 5))


