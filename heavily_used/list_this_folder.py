import os
import argparse
import natsort


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-path", type=str)
    args = parser.parse_args()

    with open("./file_in_this_folder.txt", "w") as f:
        f.write("")

    file_list = os.listdir(args.root_path.replace(os.sep, "/"))
    sorted_file_list = natsort.natsorted(file_list, key=str.lower)

    with open(
        "./file_in_this_folder.txt", "a", encoding="utf-8"
    ) as f:  # 인코딩을 utf-8로 설정
        for filename in sorted_file_list:
            name, ext = os.path.splitext(filename)
            f.write(f"{name}\n")

    print("Done.")


if __name__ == "__main__":
    main()
