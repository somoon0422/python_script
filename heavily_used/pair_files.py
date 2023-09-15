import os, sys

global total_error
global total_img
global total_txt
total_error = 0
total_img = 0
total_txt = 0


def check_fileExtension(img_path):
    mylist = [".jpg", ".png", ".JPG", ".PNG", ".jpeg"]
    cnt = 0
    for item in mylist:
        img_file = img_path + item
        if os.path.isfile(img_file):
            break
        else:
            cnt += 1
    if cnt == 5:
        img_file = "None"
    return img_file


def match_files(data_dir):
    global total_error
    global total_img
    global total_txt

    files = os.listdir(data_dir)

    # save_list = open('D:/image/220914_NIPA_NEW/no_list.txt', 'a')
    # save_list = open('D:/image/aihub_excavator/Training/no_list.txt', 'a')

    for file in files:
        fileName, fileExtension = os.path.splitext(file)
        path_onefile = os.path.join(data_dir, file)

        # case1) dir
        if os.path.isdir(path_onefile):
            # print('file : ', file, 'is directory. find sub-directory...')
            match_files(path_onefile)

        # case2) file
        if fileExtension == ".txt":
            total_txt += 1
            img_path = data_dir + "/" + fileName
            img_file = check_fileExtension(img_path)
            if img_file == "None":
                # print('Not exist img file! - ' + data_dir + '/' + file)
                os.chmod(data_dir + "/" + file, 755)
                os.remove(data_dir + "/" + file)
                total_error += 1
                # save_list.write(data_dir + '/' + file + '\n')

            if (
                fileExtension == ".jpg"
                or fileExtension == ".JPG"
                or fileExtension == ".png"
                or fileExtension == ".PNG"
                or fileExtension == ".jpeg"
            ):
                total_img += 1
                txt_path = data_dir + "/" + fileName + ".txt"
                #     if not os.path.isfile(txt_path):
                # print('Not exist txt file! - ' + data_dir + '/' + file)
                os.chmod(data_dir + "/" + file, 755)
                os.remove(data_dir + "/" + file)
                total_error += 1

    #             save_list.write(data_dir + '/' + file + '\n')

    # save_list.close()


def main(argv):
    data_dir = argv[0]
    match_files(data_dir)

    print("task Done!\n")

    print(" * total image : " + str(total_img))
    print(" * total text : " + str(total_txt))
    print(" *** total not match : " + str(total_error))

    print("=" * 50)


if __name__ == "__main__":
    argvsize = 2
    if len(sys.argv) < argvsize:
        print("usage : python pair_files.py data_dir")
    else:
        main(sys.argv[1:])
