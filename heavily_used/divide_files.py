
import os, sys, shutil
import argparse

from tqdm import tqdm


"""
root-path 안의 파일을 split개만큼 쪼개서 폴더로 분리하는 코드
텍스트도 같이 옮겨진다
"""


def read_files(path, exts):
    files = []
    
    for r, d, f in os.walk(path):
        for file in f:
            if file.lower().endswith(exts):
                file = os.path.join(r, file)
                file = os.path.abspath(file)
                file = file.replace(os.sep, "/")
                files.append(file)
            
    return files


def split(files, root_path, split_cnt):
    cnt = 0
    folder_cnt = 1
    
    for file in tqdm(files):
        name, _ = os.path.splitext(file)
        txt = name + ".txt"
        
        cnt += 1
        
        current_folder = os.path.split(root_path)[-1]
        new_path = os.path.join(root_path, f"{current_folder}_{folder_cnt:03d}")
        
        if not os.path.isdir(new_path):
            os.mkdir(new_path)
        
        # 이미지와 텍스트 옮기기
        if os.path.isfile(file):
            shutil.move(file, new_path)
            
            if os.path.isfile(txt):
                shutil.move(txt, new_path)
        
        if cnt == split_cnt:
            cnt = 0
            folder_cnt += 1



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--root-path")
    parser.add_argument("--split")
    
    args = parser.parse_args()
    
    ROOT = args.root_path.replace(os.sep, "/")
    SPLIT = int(args.split)
    
    images = read_files(ROOT, exts=(".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP",".avi"))
    
    split(images, ROOT, SPLIT)
    
    print("Done!")
    



