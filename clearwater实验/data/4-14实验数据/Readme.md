scp -r -P 9000 root@100.64.249.217:/root/data ./

rm ./data/*-labeled.xls
./label.py ./data/host10274.xlsx node23.log
./label.py ./data/host10280.xlsx node29.log
./label.py ./data/host10283.xlsx node32.log