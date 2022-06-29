## Block Log Compression Dictionaries

This repo contains dictionaries used for compressing blocks.  Since blocks are relatively
short and tend to have significant amounts of similar data from block to block, using 
custom compression dictionaries significantly improves compression.  In testing, we 
found a ~4.5% improvement in compression ratio using the custom dictionaries.  At the 
current block log size, that saves about 25GB.

Since the contents of blocks (active accounts, popular operations, etc) varies over time,
we have a different pre-computed dictionary for each million blocks (1M blocks is roughly
one month worth).

These dictionaries are stored in a submodule to reduce the size of the main hive repo. 
The dictionaries currently consume about 9MB, but they are only useful for the hive
mainnet.  The testnet builds or other chains that don't have the same blocks as hive
will not get much benefit from these dictionaries, so the testnet can be built without
them.

## Procedure for generating dictionaries

It's assumed that:
 - existing dictionaries are never changed, so you'll always be able to decode your old
   block logs with newer builds of hived
 - each time a new major release of Hive is made, we'll generate new optimal dictionaries 
   for the millions of blocks generated since the previous major release, and they will
   be added to this repository

#### Extract a million blocks

Use the `compress_block_log` utility to extact each block in the range you're interested in
and store it in a separate file.  Run something like:

```
rm -r /tmp/blockchain
compress_block_log --decompress --input-block-log=/storage1/datadir/blockchain --output-block-log=/tmp/blockchain --starting-block-number=60000000 --block-count=1000000 --dump-raw-blocks=/tmp/blocks
```

This will create one million files on your disk, each containing a block.  They'll be laid out with one directory per
million files.  Inside the directories, the files will be split by the hundred-thousand to be kind to the filesystem.

```
/tmp/blocks/60000000/60000000/60000000.bin
/tmp/blocks/60000000/60000000/60000001.bin
...
/tmp/blocks/60000000/60000000/60099999.bin
/tmp/blocks/60000000/60100000/60100000.bin
```

#### Take a random sample of blocks

The tool for creating dictionaries can only process up to 2GB of input, so it's not possible to feed it a full million
blocks.  We'll randomly choose blocks that add up to 2GB total, and create a dictionary based on those.  

```
utils/sample_blocks.py /tmp/blocks/60000000 /tmp/blocks-randomsample/60000000 2147483648
```

#### Compute a dictionary from the sample

We've settled on using 220K dictionaries optimized for compression level 15, generated thus:
```
zstd -T0 -r --train-fastcover /tmp/blocks-randomsample/60000000 -15 --maxdict=225280 -o /tmp/dictionaries/220K/060M.dict --dictID=60
```

#### Compress the dictionary

```
zstd -v --ultra -22 /tmp/dictionaries/220K/060M.dict
```

#### Update CMakeLists.txt

Update the CMakeLists.txt to reference the new last dictionary number you just added
```
FOREACH(DICTIONARY_NUM RANGE 60)
```
