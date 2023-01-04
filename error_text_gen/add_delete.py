import random
random.seed(33)

class AddDelete:
    def __init__(self) -> None:
        pass

    def error_text(self, text, pos=0, cand_num=1):
        poses = [i for i in range(len(text))]
        cho = random.random()
        # 随机选择删除、添加和交换操作
        if cho < 1/3: #删除pos上的字符
            return [text[:pos]+text[pos+1:]]
        elif cho < 2/3: #添加，将pos位置的字符添加到其他位置上去
            add_pos = random.choice(poses)
            return [text[:add_pos]+ text[pos]+text[add_pos:]]
        else:#乱序
            #删除原有的pos
            poses = list(set(poses)-set([pos]))
            swap_pos = random.choice(poses)
            text_li = list(text)
            text_li[swap_pos], text_li[pos] = text_li[pos], text_li[swap_pos]
            return ["".join(text_li)]


            


