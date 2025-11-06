import os
import re
import argparse
import uuid

data_dir = "/home/theslender/coding_stuff/Uni_documents/morty_chall/planet_2_Purge_runs_20251106_200714"

# Usage: call script with --shift N to add N to the run number (default 10).
# Example to rename run_001 -> run_011: python temp.py --shift 10
parser = argparse.ArgumentParser(description="Shift run_###.json filenames by a given offset.")
parser.add_argument("--shift", type=int, default=10, help="How much to add to the run number (can be negative).")
parser.add_argument("--pad", type=int, default=3, help="Zero-padding width for the run number.")
parser.add_argument("--dry-run", action="store_true", help="Show planned renames without performing them.")
args = parser.parse_args()

pattern = re.compile(r"^(run_)(\d{3})(\.json)$", re.IGNORECASE)

# Collect files to rename
entries = []
for name in os.listdir(data_dir):
    m = pattern.match(name)
    if not m:
        continue
    prefix, num_str, ext = m.groups()
    old_num = int(num_str)
    new_num = old_num + args.shift
    if new_num < 0:
        raise ValueError(f"Resulting run number for {name} would be negative ({new_num})")
    new_name = f"{prefix}{str(new_num).zfill(args.pad)}{ext}"
    if new_name == name:
        continue
    entries.append((name, new_name))

if not entries:
    print("No matching files to rename.")
    exit(0)

# Print plan
print("Planned renames:")
for old, new in entries:
    print(f"  {old} -> {new}")
if args.dry_run:
    print("Dry run enabled; no files will be modified.")
    exit(0)

# First pass: rename to unique temporary names to avoid collisions
tmp_map = {}
for old, _ in entries:
    tmp_name = f".tmp_{uuid.uuid4().hex}_{old}"
    os.rename(os.path.join(data_dir, old), os.path.join(data_dir, tmp_name))
    tmp_map[tmp_name] = old  # keep mapping if needed

# Second pass: rename temps to their final targets
for old, new in entries:
    tmp_name = f".tmp_"  # find the tmp that corresponds to old
    # locate corresponding tmp file (unique prefix + old)
    matching_tmp = None
    for fname in os.listdir(data_dir):
        if fname.endswith(f"_{old}") and fname.startswith(".tmp_"):
            matching_tmp = fname
            break
    if matching_tmp is None:
        raise FileNotFoundError(f"Temporary file for {old} not found.")
    dst = os.path.join(data_dir, new)
    src = os.path.join(data_dir, matching_tmp)
    if os.path.exists(dst):
        raise FileExistsError(f"Target filename already exists: {dst}")
    os.rename(src, dst)

print("Renaming complete.")
