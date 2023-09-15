import json
import os


def json_to_txt(json_file, output_folder):  # json 파일을 txt 파일로 변환하는 함수
    with open(json_file, "r") as file:  # json 파일을 읽기 모드로 열기
        print(json_file + " is loaded...")  # json 파일이 로드되었음을 출력
        data = json.load(file)  # json 파일을 읽어서 data에 저장
    images = data["image"]  # data에서 image 정보만 가져옴
    annotations = data["annotation"]  # data에서 annotation 정보만 가져옴
    for img_info in images:
        image_name = img_info["image_name"].split(".")[0]  # image_name에서 확장자를 제거
        image_id = img_info["image_id"]  # image_id를 가져옴
        if image_id in annotations:
            with open(
                f"{output_folder}/{image_name}.txt", "w"
            ) as txt_file:  # txt 파일을 생성
                for annotation in annotations[image_id]:  # annotation 정보를 가져옴
                    if not annotation["class_id"]:
                        continue
                    class_id = annotation["class_id"][0]
                    # 사람 라벨만 저장
                    if class_id == 0:  # 0: person
                        x_top, y_top, width, height = annotation["bbox"]  # bbox 정보를 가져옴
                        x_center = x_top + width / 2  # bbox의 중심 좌표를 계산
                        y_center = y_top + height / 2  # bbox의 중심 좌표를 계산
                        txt_file.write(
                            f"{class_id} {x_center} {y_center} {width} {height}\n"
                        )  # txt 파일에 bbox 정보를 저장


def process_all_folders(base_folder):
    for root, dirs, files in os.walk(base_folder):  # base_folder의 하위 폴더들을 탐색
        for file in files:  # 하위 폴더의 파일들을 탐색
            if file.endswith(".json"):  # json 파일만 탐색
                json_path = os.path.join(root, file)  # json 파일의 경로를 가져옴
                json_to_txt(json_path, root)  # json 파일을 txt 파일로 변환


base_folder = "D:/DATA/admin/2023/2023_IITP_폭행_bbox/violence_bbox_IITP"
process_all_folders(base_folder)  # base_folder의 하위 폴더들을 탐색하여 json 파일을 txt 파일로 변환

print("Done!")
