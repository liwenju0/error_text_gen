'''
并行生成正确错误数据，以提高性能。
'''
import os 
from pipeline import GenErrorText
from tqdm import tqdm  
import sys 
import random
random.seed(33)

import logging

save_dir = "/ssd2/generate_correct_data_v2/"
ori_dir = "/ssd2/wudao_corpus/"

def gen(filename):
    print(f"进程id: {os.getpid()}, 处理文件名: {filename}")
    generator = GenErrorText()
    path = os.path.join(ori_dir, filename)
    src = []
    target = []
    cnt = 0
    file_index = 0
    for line in tqdm(open(path, errors="ignore")):
        line = line.strip()
        line = line.replace("\n", "")
        line = line.replace(" ", "")
        if len(line) < 3 or len(line) > 256:
            continue
        try:
            res = generator.generate(line)
            if res != line:
                src.append(line)
                target.append(res)

            if len(src) == 100*10000:
                file_index += 1
                src_file = os.path.join(save_dir, f'{filename.split(".")[0]}_{file_index}.src')
                tgt_file = os.path.join(save_dir, f'{filename.split(".")[0]}_{file_index}.tgt')
                print(f"writing {src_file}  {tgt_file}")
                
                with open(src_file, "w") as f:
                    f.write("\n".join(src))
                with open(tgt_file, "w") as f:
                    f.write("\n".join(target))
                
                src = []
                target = []       

        except Exception as e:
            cnt += 1
            logging.exception(e)
            print("进程：", os.getpid(), e, "正在处理的句子是" ,line, "异常次数为：", cnt)


if __name__ == "__main__":
    f = sys.argv[1]
    print(f"启动进程处理文件: {f}")
    gen(f)
            

        
        

