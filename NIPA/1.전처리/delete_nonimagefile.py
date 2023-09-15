import os
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process log.txt file")
    parser.add_argument(
        "--path", type=str, help="Path to the directory containing log.txt"
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    log_file_path = os.path.join(args.path, "log.txt")

    if not os.path.exists(log_file_path):
        print(f"log.txt file not found in {args.path}")
        return

    with open(log_file_path, "r", encoding="utf-8") as log_file:
        lines = log_file.readlines()

    new_lines = []
    for line in lines:
        line = line.strip()
        file_name = line.split("/")[-1]  # Get the last part of the path
        new_lines.append(file_name)

    new_file_path = os.path.join(args.path, "file_names.txt")
    with open(new_file_path, "w") as new_file:
        new_file.write("\n".join(new_lines))

    print(f"Processed log.txt and created file_names.txt in {args.path}")


if __name__ == "__main__":
    main()
