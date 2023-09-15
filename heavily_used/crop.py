"""
python crop.py --root {데이터셋 절대경로}
"""

import os
import cv2
import numpy as np
import argparse
from pathlib import Path
from tqdm import tqdm

import warnings

warnings.filterwarnings(action="ignore")


def load_images_path(root):
    images_path = []

    for r, d, f in os.walk(root):
        for file in f:
            if file.lower().endswith((".jpg", ".png", ".bmp", ".jpeg")):
                images_path.append(os.path.join(r, file).replace(os.sep, "/"))

    return images_path


def load_labels_path(root):
    labels_path = []

    for r, d, f in os.walk(root):
        for file in f:
            if file.lower().endswith(".txt"):
                labels_path.append(os.path.join(r, file).replace(os.sep, "/"))

    return labels_path


parser = argparse.ArgumentParser(
    description="Crop Bounding Boxes(as ROI) and save them"
)
parser.add_argument("--root", type=str, required=True)

args = parser.parse_args()

labeled_dataset_root_dir = args.root
images_path = load_images_path(labeled_dataset_root_dir)
labels_path = load_labels_path(labeled_dataset_root_dir)

assert len(images_path) == len(labels_path)

for images_path, label_path in zip(images_path, labels_path):
    image_name = Path(images_path).resolve().stem
    folder_name = str(Path(images_path).resolve().parent).split("\\")[-1]
    image_name = folder_name + "__" + image_name

    image = cv2.imread(images_path)
    if image is None:
        print(f"OenCV failed to decode {images_path}")
        continue

    image_draw = image.copy()

    label = np.loadtxt(label_path, dtype=np.float32, delimiter=" ")
    label = label.reshape(-1, 5)

    # yolo format: c x y w h
    classes = label[:, 0].reshape(-1, 1).astype(np.long)
    bboxes = label[:, 1:5].reshape(-1, 4)

    for i, (c, bbox) in enumerate(zip(classes, bboxes)):
        c = c.item()

        if int(c) == 99:
            continue

        x, y, w, h = bbox

        x, w = bbox[[0, 2]] * image.shape[1]
        y, h = bbox[[1, 3]] * image.shape[0]

        xmin = x - w / 2
        xmax = x + w / 2

        ymin = y - h / 2
        ymax = y + h / 2

        xmin, xmax = np.clip([xmin, xmax], 0, image.shape[1] - 1).astype(np.int)
        ymin, ymax = np.clip([ymin, ymax], 0, image.shape[0] - 1).astype(np.int)

        data_folder = os.path.join(args.root, "dataset", str(c))
        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)
            print("\nmakedir :", str(c), end="")

        # print(image_name)
        cv2.imwrite(
            os.path.join(data_folder, image_name + str(i) + ".jpg"),
            image[ymin:ymax, xmin:xmax],
        )

        if c == 0:
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        elif c == 1:
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
        elif c == 2:
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
        elif c == 3:
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (255, 255, 0), 2)
        elif c == 4:
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (0, 255, 255), 2)
        else:
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (255, 0, 255), 2)

    # cv2.imshow("image_draw", image_draw)
    if cv2.waitKey(1) == 27:  # Esc
        break
