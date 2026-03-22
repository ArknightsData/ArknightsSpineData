"""Standalone python script to download arknights spine assets from Harry Huang's repo, render them in a consistent resolution and upload them to a branch of the current repository.

Requires: python 3.9+, python's requests, .NET 8.0, ffmpeg spine_asset

Original script belongs to ashleney
"""

import io
import json
import os
import subprocess
import shutil
import zipfile

import requests
from spine_asset.v38 import SkeletonBinary


branch = "cn"

# checkout the actual asset branch
subprocess.run(["git", "fetch", "--depth=1", "origin", f"{branch}:{branch}"], check=True)
subprocess.run(["git", "checkout", branch], check=True)

# download resources
for url, destination in (
    ("https://github.com/ashleney/SpineExporter/releases/download/0.0.3/SpineExporter.zip", "SpineExporter"),
    ("https://github.com/isHarryh/Ark-Models/archive/refs/heads/main.zip", "Ark-Models-main"),
):
    if os.path.exists(destination):
        continue

    print(f"Downloading {url}")
    response = requests.get(url)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall()

with open("Ark-Models-main/models_data.json", encoding="utf-8") as file:
    models_data = json.load(file)


for name, entry in models_data["data"].items():
    filenames: dict[str, str] = {k: v[0] if isinstance(v, list) else v for k, v in entry["assetList"].items()}
    if entry["type"] == "Operator":
        source_directory = os.path.join("Ark-Models-main", "models", name)
        print(os.path.join(source_directory, filenames['.skel']))
        with open(os.path.join(source_directory, filenames['.skel']), "rb") as f:
            skeleton_data = SkeletonBinary().read_skeleton_data(f.read())
        for a in skeleton_data.animations:
            output_directory = os.path.join("operator", a.name)
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, filenames[".atlas"].replace(".atlas", ".webm"))
            if os.path.exists(output_path):
                continue
                
            subprocess.run(
                f"SpineExporter\\SpineExporter.exe "
                f"--skel {os.path.join(source_directory, filenames['.skel'])} "
                f"--atlas {os.path.join(source_directory, filenames['.atlas'])} "
                f'--output {output_path} '
                f'--animation {a.name} '
                f"--pma "
                f"--fps 24 "
                f"--loop "
                f"--width 1024 "
                f"--height 576 "
                f"--centerx 0 "
                f"--centery 288",
                check=True,
            )

    elif entry["type"] == "DynIllust":
        source_directory = os.path.join("Ark-Models-main", "models_illust", name)
        with open(os.path.join(source_directory, filenames['.skel']), "rb") as f:
            skeleton_data = SkeletonBinary().read_skeleton_data(f.read())
        for a in skeleton_data.animations:
            output_directory = os.path.join("illust", a.name)
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, filenames[".atlas"].replace(".atlas", ".webm"))
            if os.path.exists(output_path):
                continue

            print(output_path)
            subprocess.run(
                f"SpineExporter/SpineExporter.exe "
                f"--skel {os.path.join(source_directory, filenames['.skel'])} "
                f"--atlas {os.path.join(source_directory, filenames['.atlas'])} "
                f'--output {output_path} '
                f'--animation {a.name} '
                f"--pma "
                f"--fps 24 "
                f"--crf 40 "
                f"--loop "
                f"--width 1024 "
                f"--height 1024 "
                f"--centerx 0 "
                f"--centery 1024 "
                f"--zoom 0.5",
                check=True,
            )
        
        
    elif entry["type"] == "Enemy":
        source_directory = os.path.join("Ark-Models-main", "models_enemies", name)
        with open(os.path.join(source_directory, filenames['.skel']), "rb") as f:
            skeleton_data = SkeletonBinary().read_skeleton_data(f.read())
        for a in skeleton_data.animations:
            output_directory = os.path.join("enemies", a.name)
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, filenames[".atlas"].replace(".atlas", ".webm"))
            if os.path.exists(output_path):
                continue

            print(output_path)
            subprocess.run(
                f"SpineExporter\\SpineExporter.exe "
                f"--skel {os.path.join(source_directory, filenames['.skel'])} "
                f"--atlas {os.path.join(source_directory, filenames['.atlas'])} "
                f'--output {output_path} '
                f'--animation {a.name} '
                f"--pma "
                f"--fps 24 "
                f"--loop "
                f"--width 1024 "
                f"--height 576 "
                f"--centerx 0 "
                f"--centery 288",
                check=True,
            )


if (os.path.exists(os.path.join(os.getcwd(),"Ark-Models-main"))):
    shutil.rmtree(os.path.join(os.getcwd(),"Ark-Models-main"))

if (os.path.exists(os.path.join(os.getcwd(),"SpineExporter"))):
    shutil.rmtree(os.path.join(os.getcwd(),"SpineExporter"))

toSearch = {
    'enemies': [],
    'illust': [],
    'operator': []
}

for paths in toSearch:
    toSearch[paths] = os.listdir(os.path.join(os.getcwd(), paths))

json_str = json.dumps(toSearch, indent=4)
with open("output.json", "w") as f:
    f.write(json_str)



subprocess.run(["git", "add", "build", "illust"], check=True)
if not subprocess.check_output(["git", "diff", "--cached", "--name-only"]).strip():
    print("Nothing exported")
    exit(0)

subprocess.run(["git", "commit", "-m", "update"], check=True, stdout=subprocess.DEVNULL)
subprocess.run(["git", "push", "origin", branch], check=True)
subprocess.run(["git", "checkout", "master"], check=True)
