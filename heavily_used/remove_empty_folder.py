
import os, sys, shutil
import argparse

from tqdm import tqdm


"""
빈 폴더 삭제하기
*폴더 A 안에 빈 폴더 B가 있으면 B만 삭제됨 (A는 내용물이 있는 폴더로 간주됨)
"""


def read_folders(path):
    folders = []
    
    for r, d, f in os.walk(path):
        for folder in d:
                folder = os.path.join(r, folder)
                folder = os.path.abspath(folder)
                folder = folder.replace(os.sep, "/")
                folders.append(folder)
            
    return folders



def remove_empty(folders):
    
    for folder in folders:
        childrens = os.listdir(folder)
        if not childrens:
            shutil.rmtree(folder)



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-path")
    
    args = parser.parse_args()
    ROOT = args.root_path.replace(os.sep, "/")
    folders = read_folders(ROOT)
    
    remove_empty(folders)
    
    print("Done!")        



