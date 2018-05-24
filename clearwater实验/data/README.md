# 取回实验数据

scp -r -P 9000 root@100.64.249.217:/root/data ./


# 打标签
../label.py data/host10274.xlsx node23_stress.log
../label.py data/host10280.xlsx node26_stress.log
../label.py data/host10283.xlsx node32_stress.log