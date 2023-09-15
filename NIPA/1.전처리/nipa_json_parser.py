# nipa에서 제공한 json 파일을 읽어서 YOLO형식의 txt 파일로 저장
# json 파일 하나에 비디오 하나의 정보가 있음

# 사용법 : python nipa_json_parser.py --root 폴더 --1 --2 --3 --4
# --root 옵션 자리에는 데이터가 모두 들어 있는 상위 폴더를 지정
# --1 / --2 / --3 / --4 옵션을 사용하여 원하는 작업만 수행할 수 있음 (여러 개 동시에도 가능)


import os, sys, json, argparse
import multiprocessing

import cv2
import shutil

from tqdm import tqdm
from collections import defaultdict


exts = (".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP")


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


def read_folders(path):
    folders = []

    for r, d, f in os.walk(path):
        for folder in d:
            folder = os.path.join(r, folder)
            folder = os.path.abspath(folder)
            folder = folder.replace(os.sep, "/")
            folders.append(folder)

    return folders


# 중복 라벨링 방지하기 위하여 텍스트 파일 삭제
def remove_txt(path_src):
    files = read_files(path_src, ".txt")
    for file in files:
        if "no_image_list" in file:
            continue
        os.remove(file)


def count_attribute(path_src):
    files = read_files(path_src, ".json")

    total_img = 0
    total_bbox = 0
    no_image_list = []
    attributes_list = []

    for file in files:
        if "crop_dataset" in file:
            continue

        with open(file, "r", encoding="utf-8-sig") as f:
            jd = json.load(f)  # json 파일 내용 불러오기

        # filename과 id 일치시키기
        image_dict = {}
        for one_image in jd["images"]:
            total_img += 1
            file_name = one_image["file_name"]
            id = one_image["id"]
            image_dict[id] = file_name

        # bbox 정보 구하기
        for one_obj in jd["annotations"]:
            image_id = one_obj["image_id"]

            # ../images 폴더에 해당 이미지가 있는지 확인. 없으면 에러 로그 기록.
            img_path = (
                os.path.split(file)[0].replace("annotations", "images")
                + "/"
                + image_dict[image_id]
            )

            if not os.path.isfile(img_path):
                no_image_list.append(img_path)

            # 태그 하나씩 순회
            if image_id in image_dict:
                total_bbox += 1

                attributes = one_obj["attributes"]  # 각 속성이 몇 개인지 세기
                ignore_attributes = [
                    "occluded",
                    "rotation",
                    "track_id",
                    "keyframe",
                    "ID",
                    "actor_id",
                ]  # 카운트에서 제외할 속성들

                for attrib in attributes:
                    if not attrib in ignore_attributes:
                        value = str(attributes[attrib])
                        attri_name = (
                            attrib + "___" + value
                        )  # 값이 같아도 중복되지 않게 속성+값으로 이름 설정

                        if not attri_name in attributes_list:  # 각 속성 카운트
                            attributes_list.append(attri_name)

    with open(f"{ROOT}/no_image_list.txt", "w") as f:
        for img in no_image_list:
            f.write(f"{img}\n")

    return total_img, total_bbox, no_image_list, attributes_list


def crop_img(path_src):
    if not os.path.isdir(f"{ROOT}/crop_dataset/"):
        os.mkdir(f"{ROOT}/crop_dataset/")

    files = read_files(path_src, ".json")
    for file in tqdm(files):
        if "crop_dataset" in file:
            continue

        with open(file, "r", encoding="utf-8-sig") as f:
            jd = json.load(f)

        # 이미지 파일명과 id 매칭
        image_dict = defaultdict(str)
        for one_image in jd["images"]:
            file_name = one_image["file_name"]
            id = one_image["id"]
            image_dict[id] = file_name

        for one_obj in jd["annotations"]:
            image_id = one_obj["image_id"]
            obj_id = one_obj["id"]

            try:
                if image_dict[image_id]:
                    img_path = (
                        os.path.split(file)[0].replace("annotations", "images")
                        + "/"
                        + image_dict[image_id]
                    )
                    # try:
                    img = cv2.imread(img_path)

                    # bbox 구하기 (타이트한 버전)
                    box_x = int(one_obj["bbox"][0])
                    box_y = int(one_obj["bbox"][1])
                    box_w = int(one_obj["bbox"][2])
                    box_h = int(one_obj["bbox"][3])

                    tx = (box_x - 1) if int(box_x) > 1 else 0
                    ty = (box_y - 1) if int(box_y) > 1 else 0
                    w = (box_w + 2) if int(box_w) > 2 else 0
                    h = (box_h + 2) if int(box_h) > 2 else 0

                    cropped_img = img[ty : ty + h, tx : tx + w]

                    new_path = ROOT + "/crop_dataset/" + image_dict[image_id][:-11]
                    os.makedirs(new_path + "/crops/", exist_ok=True)
                    os.makedirs(new_path + "/annotations/", exist_ok=True)

                    crop_path = f"{new_path}/crops/{image_dict[image_id]}"
                    crop_ann_path = (
                        f"{new_path}/annotations/{image_dict[image_id][:-11]}.json"
                    )

                    shutil.copyfile(file, crop_ann_path)  # json도 크롭한 이미지 폴더에 복사 (최초 1회)

                    # 사람 한 명만 등장함
                    cv2.imwrite(crop_path, cropped_img)

            except:
                img_path = (
                    os.path.split(file)[0].replace("annotations", "images")
                    + "/"
                    + image_dict[image_id]
                )
                print(f"image doesn't exist : {img_path}")


def json_to_yolo(path_src):
    files = read_files(path_src, ".json")

    total_img = 0
    total_bbox = 0

    for file in files:
        if "crop_dataset" in file:
            continue

        with open(file, "r", encoding="utf-8-sig") as f:
            jd = json.load(f)  # json 파일 내용 불러오기

        image_dict = defaultdict(str)
        for one_image in jd["images"]:
            total_img += 1

            # frame w, h 구하기
            img_w = one_image["width"]
            img_h = one_image["height"]
            file_name = one_image["file_name"]
            id = one_image["id"]

            image_dict[id] = [file_name, img_w, img_h]

        # bbox 정보 구하기

        # 현재 문제 : 어노테이션이 하나의 txt에 모두 뭉친다

        for one_obj in jd["annotations"]:
            image_id = one_obj["image_id"]

            if image_dict[image_id][0]:
                txt_path = os.path.split(file)[0].replace(
                    "annotations", "images"
                )  # 폴더 지정
                txt_path += f"/{image_dict[image_id][0][:-4]}.txt"  # 파일명 지정

                with open(txt_path, "a") as one_text:
                    img_w = image_dict[image_id][1]
                    img_h = image_dict[image_id][2]

                    x = one_obj["bbox"][0]
                    y = one_obj["bbox"][1]
                    w = one_obj["bbox"][2]
                    h = one_obj["bbox"][3]

                    x = str(round((x + (1 / 2 * w)) / img_w, 6))
                    y = str(round((y + (1 / 2 * h)) / img_h, 6))
                    w = str(round(w / img_w, 6))
                    h = str(round(h / img_h, 6))

                    # 일단 사람은 무조건 라벨링
                    one_text.write(f"{class_dict['person']} {x} {y} {w} {h}\n")
                    total_bbox += 1

                    # 추후 특정 속성을 가진 사람만 별도로 추출할 경우 아래의 코드를 수정해서 사용

                    # attributes =  one_obj['attributes']

                    # # 카운트에서 제외할 속성들
                    # ignore_attributes = ['occluded', 'rotation', 'track_id', 'keyframe', 'ID', 'actor_id']
                    # # 각 객체의 속성들을 클래스로 할당
                    # for one in attributes:
                    #     if not one in  ignore_attributes:
                    #         value = attributes[one]

                    #         # # 휠체어, 목발, 지팡이, 유모차, 캐리어 속성을 가진 사람만 라벨링 기록
                    #         # if value == 'carrier' or  value == 'wheelchair' or value == 'crutches' \
                    #         #     or value == 'cane' or value == 'walking-frame':
                    #         #     one_text.write(f"{class_dict['person']} {x} {y} {w} {h}\n")

                    #         # # 성별 가진 사람만 라벨링 기록
                    #         # if value == 'man' or  value == 'woman':
                    #         #     one_text.write(f"{class_dict[value]} {x} {y} {w} {h}\n")

                    #         # 모두 기록
                    #         if one == 'bottom_color':
                    #             value = 'bottom_' + value
                    #         if one == 'top_color':
                    #             value = 'top_' + value

                    #         if value in class_dict:
                    #             attribute_id = class_dict[value]
                    #             one_text.write(f"{attribute_id} {x} {y} {w} {h}\n")

                    # json 파일과 동일한 이름의 폴더 안에 txt 파일 생성
                    # one_text = open(path_src + '/' + fileName + '/' + image_dict[image_id][0][:-4] + '.txt', 'a')

            else:
                print(
                    f'image id [{image_id}] exists in "images", but not in "annotations"'
                )

    return total_img, total_bbox


parser = argparse.ArgumentParser()

parser.add_argument("--root", type=str, default="data")
parser.add_argument("--1", action="store_true")
parser.add_argument("--2", action="store_true")
parser.add_argument("--3", action="store_true")
parser.add_argument("--4", action="store_true")

args = parser.parse_args()
task_1 = getattr(args, "1")
task_2 = getattr(args, "2")
task_3 = getattr(args, "3")
task_4 = getattr(args, "4")
ROOT = args.root.replace(os.sep, "/")


class_dict = {
    "person": "0",
    "man": "1",
    "woman": "2",
    "boots": "3",
    "slipper": "4",
    "loafers": "5",
    "no-shoes": "6",
    "t-shirt": "7",
    "jumper": "8",
    "jacket": "9",
    "shirt": "10",
    "long-sleeve": "11",
    "short-sleeve": "12",
    "sleeveless": "13",
    "long-skirt": "14",
    "short-skirt": "15",
    "long-pants": "16",
    "short-pants": "17",
    "short-hair": "18",
    "bobbed-hair": "19",
    "long-hair": "20",
    "ponytail": "21",
    "bald": "22",
    "hat": "23",
    "helmet": "24",
    "mask": "25",
    "no-mask": "26",
    "glasses": "27",
    "sunglasses": "28",
    "no-glasses": "29",
    "wheelchair": "30",
    "crutches": "31",
    "cane": "32",
    "walking-frame": "33",
    "top_blue": "34",
    "top_black": "35",
    "top_brown": "36",
    "top_red": "37",
    "top_orange": "38",
    "top_yellow": "39",
    "top_green": "40",
    "top_beige": "41",
    "top_purple": "42",
    "top_pink": "43",
    "top_gray": "44",
    "top_white": "45",
    "top_navy": "46",
    "top_check": "47",
    "top_stripe": "48",
    "top_color-blocking": "49",
    "top_printing": "50",
    "bottom_black": "51",
    "bottom_brown": "52",
    "bottom_red": "53",
    "bottom_orange": "54",
    "bottom_yellow": "55",
    "bottom_green": "56",
    "bottom_beige": "57",
    "bottom_blue": "58",
    "bottom_purple": "59",
    "bottom_pink": "60",
    "bottom_gray": "61",
    "bottom_white": "62",
    "bottom_navy": "63",
    "bottom_pattern": "64",
    "short-strap-bag": "65",
    "long-strap-bag": "66",
    "backpack": "67",
    "carrier": "68",
    "no-bag": "69",
    "infant": "70",
    "schoolchild": "71",
    "teenager": "72",
    "young-adults": "73",
    "advanced-age": "74",
}


# 1. json 어노테이션에 총 속성이 몇 종류 있는지 카운팅
if task_1:
    print("\n[counting attribute]\n")

    total_img, total_bbox, no_image_list, attributes_list = count_attribute(ROOT)
    attributes_list.sort()
    attributes_dict = {}
    cnt = 0
    for attrib in attributes_list:
        attributes_dict[attrib] = cnt
        cnt += 1

    print(f"===== attributes_dict =====")
    for attrib in attributes_dict:
        print(f"{attrib} : {attributes_dict[attrib]}")

    print(f"\n\ntotal img : {total_img}")
    print(f"total bbox : {total_bbox}\n")

    if total_img != total_bbox:
        print("number of images and bboxes are NOT EQUAL.")
        print("maybe some annotation are missing?")

    if len(no_image_list) > 0:
        print(f"non-existing images : {len(no_image_list)}")
        print(f"check this -> {ROOT}/no_image_list.txt")

    print(f"\n{'-'*30}")


# 2. 분류 모델용 객체 크롭해서 저장
if task_2:
    print("\n[cropping images]\n")

    crop_img(ROOT)

    print(f"\n{'-'*30}")


# 3. 기존 텍스트를 다 지우고 json 포맷의 어노테이션을 yolo txt 포멧으로 변경
if task_3:
    print("\n[converting json to txt]\n")

    print("removing existing txt files...")
    remove_txt(ROOT)  # 기존 텍스트를 다 지워주는 함수 (중복 방지)

    print("converting json to txt...")
    total_img, total_bbox = json_to_yolo(ROOT)  # json 포맷의 어노테이션을 yolo txt 포멧으로 변경하는 함수

    print(f"\ntotal_img : {total_img}")
    print(f"total_bbox : {total_bbox}")
    print(f"\n{'-'*30}")


# 4. 기존 텍스트 지우기만 하고 싶을 경우
if task_4:
    print("removing existing txt files...")
    remove_txt(ROOT)  # 기존 텍스트를 다 지워주는 함수 (중복 방지)
    print(f"\n{'-'*30}")


print("\nDone!")
