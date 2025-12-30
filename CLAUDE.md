# CLAUDE.md - Compression Dictionaries Repository

## Project Overview

This repository stores pre-computed Zstandard (zstd) compression dictionaries optimized for compressing Hive blockchain blocks. Each dictionary is trained on a specific million-block range (roughly 1 month of blocks) to maximize compression efficiency.

Key benefits:
- ~4.5% improvement in compression ratio vs generic compression
- ~25GB storage savings at current block log size
- Stored as a Git submodule to keep the main Hive repo lightweight

## Tech Stack

- **Build System**: CMake 2.8.12+
- **Compression**: Zstandard (zstd) with dictionary support
- **Scripting**: Python 3 (utility scripts)
- **Integration**: C/C++ via xxd resource compilation
- **Target Library**: `hive_chain_compression_dictionaries`

## Directory Structure

```
compression_dictionaries/
├── 000M.dict.zst ... 099M.dict.zst   # Compressed dictionaries (100 files)
├── CMakeLists.txt                     # Build configuration
├── README.md                          # Usage documentation
└── utils/
    └── sample_blocks.py               # Block sampling utility
```

## Development Commands

### Generate a New Dictionary

1. Extract raw blocks from block log:
   ```bash
   compress_block_log --decompress --input-block-log=/storage/datadir/blockchain \
     --output-block-log=/tmp/blockchain --starting-block-number=60000000 \
     --block-count=1000000 --dump-raw-blocks=/tmp/blocks
   ```

2. Sample blocks (random selection up to 2GB):
   ```bash
   utils/sample_blocks.py /tmp/blocks/60000000 /tmp/blocks-randomsample/60000000 2147483648
   ```

3. Train dictionary (220K size, level 15):
   ```bash
   zstd -T0 -r --train-fastcover /tmp/blocks-randomsample/60000000 -15 \
     --maxdict=225280 -o /tmp/dictionaries/220K/060M.dict --dictID=60
   ```

4. Compress dictionary for storage:
   ```bash
   zstd -v --ultra -22 /tmp/dictionaries/220K/060M.dict
   ```

5. Update `CMakeLists.txt` RANGE parameter to include new dictionary

### Build Library (when used as submodule)

Standard CMake build:
```bash
mkdir build && cd build
cmake ..
make
```

## Key Files

| File | Purpose |
|------|---------|
| `CMakeLists.txt` | Compiles binary dictionaries into C++ source via xxd |
| `XXXM.dict.zst` | Compressed dictionary for block range XXX million |
| `utils/sample_blocks.py` | Random block sampling for training sets |

## Coding Conventions

- **Dictionary naming**: `XXXM.dict.zst` (zero-padded, e.g., `060M.dict.zst`)
- **Dictionary IDs**: Match block range (dictID=60 for 60M blocks)
- **Dictionary size**: Standard 220K (225,280 bytes)
- **Compression levels**:
  - Level 15 for dictionary training
  - Level 22 (ultra) for storing dictionaries
- **CMake patterns**: FOREACH loops with zero-padding for dictionary iteration

## CI/CD Notes

No CI pipeline - this is a data-only submodule. New dictionaries are added manually as the blockchain grows (approximately monthly for each new million blocks).

## Integration

Used as a Git submodule in the main Hive repository. The CMake build generates:
- `compression_dictionaries.cpp` with extern C declarations
- A `std::map` binding dictionary IDs to raw data and length
- Library target: `hive_chain_compression_dictionaries`
