from pysword.modules import SwordModules
import shutil
import os
import sys
import random

from settings import *
from parallel_bible import ParallelBible

# usage:
# python3 main.py VulgClementine HebModern

if __name__ == "__main__":
    m1, m2 = sys.argv[1], sys.argv[2]
    pb = ParallelBible(m1, m2)
    random_str = str(random.randint(10**10, 10**11))
    path = TMP_PATH + random_str + os.sep
    name = m1 + "_" + m2 + "_" + random_str
    pb.save_epub(name, path, res_path=RES_PATH)


    



    
