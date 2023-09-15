# 사용법: python coco_parse_v2.py --root-path [COCO 데이터셋 폴더 경로]

# 좌/우 방향키로 이미지 넘기기
# Esc 누르면 종료
# F12 누르면 현재 파일명을 {root-path}/log.txt에 기록

# 직전에 보고 있던 이미지와 현재 이미지 사이에 달라진 속성값이 있다면 해당 값을 노란 색으로 표시


import sys
import os
import argparse
from pycocotools.coco import COCO
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

WHITE = (255, 255, 255)
YELLOW = (80, 240, 255)
GREEN = (50, 200, 150)
BLACK = (0, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
SCALE = 0.5
THICKNESS = 1

# 크롭이미지 리사이즈할 크기
target_width = 350
target_height = 700

# 텍스트 여백
margin_w = 20
margin_h = 25

# 헤더(파일명 자리) 높이
header_height = 40

# 블랙 배경 이미지 너비
black_width = 300

logged = False

# 속성값 정렬용
attrib_order_col1 = [
    "inner_top_color",
    "space",
    "top_white",
    "top_gray",
    "top_black",
    "top_red",
    "top_green",
    "top_blue",
    "top_yellow",
    "top_orange",
    "top_brown",
    "top_beige",
    "top_pink",
    "top_purple",
    "top_navy",
    "top_unknown",
    "top_color-blocking",
    "top_printing",
    "top_stripe",
    "top_check",
    "space",
    "top_shape",
    "top_type",
    "space",
    "hairstyle",
    "glasses",
    "mask",
]
attrib_order_col2 = [
    "gender",
    "space",
    "btm_white",
    "btm_gray",
    "btm_black",
    "btm_red",
    "btm_green",
    "btm_blue",
    "btm_yellow",
    "btm_orange",
    "btm_brown",
    "btm_beige",
    "btm_pink",
    "btm_purple",
    "btm_navy",
    "btm_unknown",
    "btm_pattern",
    "space",
    "bottom_type",
    "space",
    "shoes",
    "age_group",
    "space",
    "walking_accessory",
    "bag",
    "space",
    "actor_id",
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Read COCO data from JSON file")
    parser.add_argument("--root-path", help="Path to the COCO JSON file")
    args = parser.parse_args()
    return args


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout


def read_coco_data(root_path):
    annotations_folder = os.path.join(root_path, "annotations")
    json_files = [f for f in os.listdir(annotations_folder) if f.endswith(".json")]

    if not json_files:
        print(f"No json files in {annotations_folder}.")
        return

    json_file = os.path.join(annotations_folder, json_files[0])

    with HiddenPrints():
        coco = COCO(json_file)
    ids = coco.imgToAnns.keys()

    idx = 1  # json에 기록된 이미지 id가 1부터 시작하기 때문에 0이 아닌 1로 초기화함
    previous_attributes = None
    while True:
        with open(f"{root_path}/log.txt", "r", encoding="utf-8") as f:
            log = f.read()

        # cv2 키보드 입력 대기
        key = cv2.waitKeyEx(0)

        if key == 0x250000:  # 왼쪽 방향키 (이전 이미지)
            idx = max(1, idx - 1)

        elif key == 0x270000:  # 오른쪽 방향키 (다음 이미지)
            idx = min(len(ids), idx + 1)

        elif key == 0x7B0000:  # F12 누르면 로그 남기기
            if image_path in log:  # 현재 이미지가 로그에 있으면 지우기
                with open(f"{root_path}/log.txt", "w", encoding="utf-8") as f:
                    log = log.replace(f"\n{image_path}", "")
                    f.write(log)

            else:  # 없으면 로그에 추가
                log += f"\n{image_path}"

                log_listed = sorted(log.split("\n"))
                log_listed = "\n".join(log_listed)

                with open(f"{root_path}/log.txt", "w", encoding="utf-8") as f:
                    f.write(log_listed)

        elif key == 27:  # Esc 누르면 종료
            cv2.destroyAllWindows()
            return

        # 이미지 정보 및 경로 가져오기
        image_info = coco.loadImgs(idx)[0]
        image_path = os.path.join(root_path, "crops", image_info["file_name"]).replace(
            os.sep, "/"
        )
        filename = image_info["file_name"].split("_")[-1]

        if not os.path.isfile(image_path):
            print(f"{image_path} doesn't exist.")
            continue

        img_h, img_w = image_info["height"], image_info["width"]
        target = coco.imgToAnns[idx]

        label = []
        num_labeled_category = 0

        if len(target) >= 2:
            print(f"len(target)={len(target)}, check {image_path} and {json_file}")
            continue

        assert len(target) == 1, print(
            f"len(target)={len(target)}, check {image_path} and {json_file}"
        )

        for obj in target:
            if "attributes" not in obj:
                continue

            if "iscrowd" in obj and obj["iscrowd"] == 1:
                continue

            if "bbox" not in obj:
                continue

            if "occluded" in obj and obj["occluded"] == True:
                continue

            attributes = obj["attributes"]

            # 이미지 로드
            img_cv2 = cv2.imread(image_path)
            height, width, _ = img_cv2.shape

            # 파일명 띄울 블랙(헤더) 이미지 생성 (상단)
            black_header = np.zeros(
                (header_height, black_width * 2 + target_width, 3), np.uint8
            )
            black_header[:] = BLACK

            # 블랙 이미지 위에 파일명 출력
            cv2.putText(
                black_header,
                f"...{filename}",
                (margin_w, margin_h),
                FONT,
                SCALE * 1.5,
                WHITE,
                THICKNESS,
            )

            if image_path in log:
                cv2.putText(
                    black_header,
                    f"logged",
                    (black_width * 2 + target_width - 100, margin_h),
                    FONT,
                    SCALE * 1.5,
                    GREEN,
                    THICKNESS,
                )

            # 속성 띄울 블랙 이미지 생성(왼쪽 열)
            black_colmn1 = np.zeros((target_height, black_width, 3), np.uint8)
            black_colmn1[:] = BLACK

            # 속성 띄울 블랙 이미지 생성(오른쪽 열)
            black_colmn2 = np.zeros((target_height, black_width, 3), np.uint8)
            black_colmn2[:] = BLACK

            # 블랙 이미지 위에 속성값을 출력
            for i, key in enumerate(attrib_order_col1):
                # 직전에 보던 페이지의 속성과 달라진 값이 있다면 노란색으로 강조 표시함
                if previous_attributes and (
                    key in previous_attributes
                    and attributes[key] != previous_attributes[key]
                ):
                    color = YELLOW
                else:
                    color = WHITE

                if key == "space":
                    cv2.putText(
                        black_colmn1,
                        " ",
                        (margin_w, margin_h * (i + 1)),
                        FONT,
                        SCALE,
                        color,
                        THICKNESS,
                    )
                else:
                    cv2.putText(
                        black_colmn1,
                        f"{key}:{attributes[key]}",
                        (margin_w, margin_h * (i + 1)),
                        FONT,
                        SCALE,
                        color,
                        THICKNESS,
                    )

            # 오른쪽 열에도 똑같이 하기
            for i, key in enumerate(attrib_order_col2):
                if previous_attributes and (
                    key in previous_attributes
                    and attributes[key] != previous_attributes[key]
                ):
                    color = YELLOW
                else:
                    color = WHITE

                if key == "space":
                    cv2.putText(
                        black_colmn2,
                        " ",
                        (margin_w, margin_h * (i + 1)),
                        FONT,
                        SCALE,
                        color,
                        THICKNESS,
                    )

                else:
                    cv2.putText(
                        black_colmn2,
                        f"{key}:{attributes[key]}",
                        (margin_w, margin_h * (i + 1)),
                        FONT,
                        SCALE,
                        color,
                        THICKNESS,
                    )

            # 필요할 경우 주석 해제
            # img_pil = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
            # img = Image.fromarray(img_pil)

            # # PIL 이미지를 다시 OpenCV 이미지로 변환
            # img_pil = np.array(img)  # PIL 이미지를 다시 OpenCV 이미지로 변환
            # img_cv2 = cv2.cvtColor(img_pil, cv2.COLOR_RGB2BGR)  # RGB to BGR

            # 이미지 리사이즈
            resized_image = cv2.resize(img_cv2, (target_width, target_height))

            # 블랙이미지1 + 블랙이미지2를 가로방향으로 합친다
            black_colmn = np.concatenate((black_colmn1, black_colmn2), axis=1)

            # 사람 크롭이미지 + (합쳐진 블랙이미지)를 가로방향으로 합친다
            black_resized_image = np.concatenate((resized_image, black_colmn), axis=1)

            # 헤더 이미지 + (크롭과 블랙이미지가 합쳐진 거)를 세로방향으로 합친다.
            black_resized_heaer_image = np.concatenate(
                (black_header, black_resized_image), axis=0
            )

            image_id = image_info["id"]

            # print(image_id)
            # print(attributes)

        previous_attributes = attributes
        cv2.imshow(f"Attribute inspection tool", black_resized_heaer_image)


def main():
    args = parse_arguments()

    # 입력한 폴더 안에 로그 파일 생성
    if not os.path.isfile(f"{args.root_path}/log.txt"):
        with open(f"{args.root_path}/log.txt", "w", encoding="utf-8") as f:
            f.write("")

    read_coco_data(args.root_path)


if __name__ == "__main__":
    main()

print("Bye!")


# def asdf(a, b):
#     return a+b

# result = asdf(1,2)
