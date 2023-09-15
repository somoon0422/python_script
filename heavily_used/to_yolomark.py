import os
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--step1", action="store_true")
parser.add_argument("--step2", action="store_true")

args = parser.parse_args()




# 파일 리스트를 읽어와서 폴더로 복사

yolo_dir = 'D:/DATA/others/check_tool/PY/modify'
# count_box -list.py 코드를 실행해서 나온 '오류 있는 파일'을 모아 놓을 폴더
# (step1을 실행하고 나면 이 폴더에 오류 있는 파일들이 복사됨)


img_list = 'D:/DATA/others/check_tool/PY/modify_list.txt'
# count_box -list.py 코드를 실행하면 생성되는 텍스트 파일 ('오류 있는 파일' 이름을 나열한 파일)


if args.step1:
    # # 원본을 YOLO_MARK에 복사
    txtFile = open(img_list, 'r')
    lines = txtFile.readlines()
    txtFile.close() 
    if len(lines) != 0:
        for line in lines:
            line = line.replace("\n", "")
            renamed = line.replace("\\", "()")
            renamed = renamed.replace("/", "()")
            renamed = renamed.replace("D:", "Ddrive")
            renamed = renamed.replace("Y:", "Ydrive")
            renamed = renamed.replace("C:", "Cdrive")
            renamed = renamed.replace("Z:", "Zdrive")
            print("===============")
            print(line)
            shutil.copy(line, yolo_dir+'/'+renamed)
            
            

elif args.step2:
    # 수정된 파일을 원본 폴더에 복사
    for renamed in os.listdir(yolo_dir):
        origin = renamed.replace("Ddrive", "D:")
        origin = origin.replace("Ydrive", "Y:")
        origin = origin.replace("Cdrive", "C:")
        origin = origin.replace("Zdrive", "Z:")
        origin = origin.replace("()", "/")
            
        shutil.move(yolo_dir + '/' + renamed, origin)

else:
    print("please input valid option.")
