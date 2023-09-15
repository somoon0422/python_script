import os, shutil
import argparse
from tqdm import tqdm

# 폴더 껍질 벗기는 코드​

def read_files(path, exts):
    files = []
    
    for r, d, f in tqdm(os.walk(path)):
        for file in f:
            if file.lower().endswith(exts):
                file = os.path.join(r, file)
                file = os.path.abspath(file)
                file = file.replace(os.sep, "/")
                files.append(file)
    return files


parser = argparse.ArgumentParser()
parser.add_argument("--root-path", type=str)

args = parser.parse_args()

root = args.root_path
files = os.listdir(root)


for file in tqdm(files):
    file_path = os.path.join(root, file)
    
    if os.path.isfile(file_path):
        continue
    
    same_file_idx = 1
    
    files_in_file = os.listdir(file_path)
    for subfile in files_in_file:
        subfile_path = os.path.join(file_path, subfile)
        
        # 라벨 파일(txt, json)은 일단 contine하고 이미지 옮길 때 한꺼번에 옮겨지도록
        subfile_name, ext = os.path.splitext(subfile_path)        
        if ext == ".json" or ext == ".txt":
            continue
        
        txt_path = subfile_name + ".txt"
        json_path = subfile_name + ".json"
        
        # root랑 subfile을 바로 연결
        new_path = os.path.join(root, subfile)
        new_txt_path = os.path.splitext(new_path)[0] + ".txt"
        new_json_path = os.path.splitext(new_path)[0] + ".json"
        
        
        # 중복 방지
        if os.path.isdir(new_path):
            new_path = f"{new_path}_({same_file_idx})"
            same_file_idx += 1
        
        elif os.path.isfile(new_path):
            name, ext = os.path.splitext(new_path)
            new_name = f"{name}_({same_file_idx})"
            
            new_path = new_name + ext
            new_txt_path = new_name + ".txt"
            new_json_path = new_name + ".json"
            
            same_file_idx += 1
        
        os.replace(subfile_path, new_path)
        
        if os.path.isfile(txt_path):
            os.replace(txt_path, new_txt_path)
        
        if os.path.isfile(json_path):
            os.replace(json_path, new_json_path)



print("Done.")