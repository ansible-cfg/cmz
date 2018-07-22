#!/bin/bash -eux

# This is to compress the image to a smaller size, due to a contigous block of zeroes on the partition

# Zero out the rest of the free space using dd, then delete the written file.
dd if=/dev/zero of=/EMPTY bs=1M
rm -f /EMPTY

# Add `sync` so Packer doesn't quit too early, before the large file is deleted.
sync
