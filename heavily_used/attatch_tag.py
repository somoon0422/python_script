import os, sys, shutil
import argparse
import tqdm

"""
인자 목록 : --root-path --tag --position

root에 해당하는 경로 내의 파일/폴더명의 position(front / back)에 tag에 해당하는 문자열 붙이기

ex) tag : "rework" / position : "back"
                   
spam_1     ->     spam_1_rework 
ham        ->     ham_rework              
bar.txt    ->     bar_rework.txt


ex) tag : "child" / position : "front"
                   
spam_1     ->     child_spam_1 
ham        ->     child_ham           
bar.txt    ->     child_bar.txt
"""




def attach_tag(files, root, tag, position):
    for file in tqdm.tqdm(files):
        file_path = os.path.join(root, file)
        new_path = ""
        
        # 폴더
        if os.path.isdir(file_path):
            if position == "front":
                new_path = f"{root}/{tag}_{file}"
            else:
                new_path = f"{root}/{file}_{tag}"
        
        # 파일
        elif os.path.isfile(file_path):
            if position == "front":
                new_path = f"{root}/{tag}_{file}"
            else:
                name, ext = os.path.splitext(file)
                new_path = f"{root}/{name}_{tag}{ext}"
                
        if new_path:
            os.rename(file_path, new_path)



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-path")
    parser.add_argument("--tag")
    parser.add_argument("--position")
    
    args = parser.parse_args()
    ROOT = args.root_path.replace(os.sep, "/")
    
    files = os.listdir(ROOT)
    
    attach_tag(files, ROOT, args.tag, args.position)
    
    
    print("Done!")
