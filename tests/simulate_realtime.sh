#!/bin/bash
# for file in /mnt/c/Users/cnj678/Desktop/remtrain999_1_data/*dcm; do
#     mv "$file" /mnt/c/Users/cnj678/Desktop/instabrain_05292025/data/dump/
#     sleep 2
# done

for file in ~/remtrain998_2_data/*.dcm; do
    cp "$file" ~/instabrain_data_dump/
    sleep 2
done
