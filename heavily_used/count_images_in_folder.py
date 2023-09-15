import os
import glob


def count_images_in_folders(parent_path):
    subfolders = os.listdir(parent_path)
    total_image_count = 0  # 전체 이미지 개수를 저장할 변수 초기화

    for subfolder in subfolders:
        subfolder_path = os.path.join(parent_path, subfolder)
        if os.path.isdir(subfolder_path):
            image_count = count_images_in_subfolders(
                subfolder_path
            )  # 각 폴더의 이미지 개수를 반환받습니다.
            total_image_count += image_count  # 전체 이미지 개수에 추가합니다.

    print(f"전체 이미지 개수: {total_image_count}")

    # 결과를 파일에 저장합니다.
    result_file = os.path.join(parent_path, "count_images.txt")
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(f"전체 이미지 개수: {total_image_count}\n")


def count_images_in_subfolders(folder_path):
    images_folder = os.path.join(folder_path, "images")
    image_count = 0

    if os.path.exists(images_folder) and os.path.isdir(images_folder):
        image_files = glob.glob(
            os.path.join(images_folder, "*.png")
        )  # 확장자가 .png 인 이미지 파일들을 찾습니다.
        image_count = len(image_files)
        folder_path_result = folder_path.split("\\")[-1]
        print(f"{folder_path_result} : {image_count}")

    subfolders = os.listdir(folder_path)

    for subfolder in subfolders:
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            image_count += count_images_in_subfolders(
                subfolder_path
            )  # 재귀적으로 각 하위 폴더의 이미지 개수를 더합니다.

    return image_count  # 각 폴더의 이미지 개수를 반환합니다.


if __name__ == "__main__":
    parent_path = (
        "D:\\DATA\\admin\\2023\\2023_스뱅_NIPA\\0728 데이터셋"  # 실제 부모 폴더 경로로 바꿔주세요.
    )
    count_images_in_folders(parent_path)


# D:\\DATA\\admin\\2023\\2023_스뱅_NIPA\\0623 데이터셋
