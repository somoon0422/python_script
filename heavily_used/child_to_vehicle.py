import os, argparse
from tqdm import tqdm


def read_files(path, exts):
    files = []

    for r, d, f in tqdm(os.walk(path)):
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


parser = argparse.ArgumentParser()
parser.add_argument("--root")
args = parser.parse_args()

folders = read_folders(args.root)
for folder in folders:
    files = read_files(folder, exts=".txt")

    for file in files:
        new_lines = []
        with open(file, "r") as f:
            lines = f.readlines()

            for line in lines:
                label, cx, cy, w, h = line.split()

                if label == "7":
                    label = "8"

                new_line = f"{label} {cx} {cy} {w} {h}"
                new_lines.append(new_line)

        with open(file, "w") as f:
            f.write("\n".join(new_lines))

print("Done.")
