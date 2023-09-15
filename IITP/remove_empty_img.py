
# 라벨이 하나도 없는 이미지 삭제

import os,sys

global total
total = 0

def emptyimg(txt_folder):
    global total 
    files = os.listdir(txt_folder)
    
    for file in files:    
        fileName, fileExtension = os.path.splitext(file)
        path_txtfile = os.path.join(txt_folder, file)
        
        # case1) dir
        if os.path.isdir(path_txtfile):
            emptyimg(path_txtfile)
        
        # case2) file
        if fileExtension == '.txt':
            txtFile = open(txt_folder + '/' + file, 'r')
            lines = txtFile.readlines()
            txtFile.close()

            if len(lines) == 0:
                # save_list = open('E:/NIPA-2/empty_list.txt', 'a')
                # save_list.write(txt_folder + '/' + file + '\n')
                # save_list.close()

                os.remove(txt_folder + '/' + file)
                try:
                    os.remove(txt_folder + '/' + fileName + '.png')
                except:
                    print('fail to remove : ' + txt_folder + '/' + fileName + '.png')
                    pass
                    # os.remove(txt_folder + '/' + fileName + '.PNG')
                # print(txt_folder + '/' + file)

                total += 1

def main(argv):
    txt_folder = argv[0]
    emptyimg(txt_folder)
    print('task Done!\n')
    print(' *** total remove : ' + str(total))
    print('='*50)
    
if __name__ == "__main__":
    argvsize = 2
    if len(sys.argv) < argvsize:
        print("usage : python remove_emptyimg.py txt_folder")
    else:
        main(sys.argv[1:])
