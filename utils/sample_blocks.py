#! /usr/bin/env python3

# Chooses a random set of blocks that add up to no more than a given size,
# used to generate the training set for creating compression dictionaries

import os
import random
import shutil
import sys

if len(sys.argv) != 4:
    print('usage:', sys.argv[0], 'src_dir', 'dest_dir', 'target_size')
    sys.exit(1)

src_dir = sys.argv[1]
dest_dir = sys.argv[2]
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

all_files = []
target_size = int(sys.argv[3])
print('Scanning files...')
for path, dirnames, filenames in os.walk(src_dir):
    all_files.extend([path + '/' + filename for filename in filenames])

print('Found', len(all_files), 'files')
selected_files = set()
total_size = 0
# this algorithm is really bad when the total size of src_dir is smaller
# than (or not much larger than) target_size.  But we only need to use
# it on the small blocks once.
while len(selected_files) < len(all_files):
    index = random.randint(0, len(all_files) - 1)
    file_path = all_files[index]
    if file_path in selected_files:
        continue
    file_size = os.path.getsize(file_path)
    if total_size + file_size > target_size:
        break

    total_size += file_size
    selected_files.add(file_path)

print('Selected', len(selected_files), 'at random that add up to', total_size, 'bytes')
print('Copying to destination')
for file_path in selected_files:
    shutil.copy(file_path, dest_dir)
print("Done")
