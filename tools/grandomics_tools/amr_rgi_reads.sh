#! /bin/bash

#. $GALAXY_CONDA_PREFIX/etc/profile.d/conda.sh
#conda activate rgi
export PATH=/opt/conda/envs/rgi/bin:$PATH

card_path=$1
r1=$2
r2=$3
aligner=$4
output_prefix=$5
threads=$6

/opt/conda/envs/rgi/bin/rgi load -i ${card_path}/card.json  --card_annotation ${card_path}/card_database_v3.0.8.fasta --local

/opt/conda/envs/rgi/bin/rgi bwt --read_one ${r1} --read_two ${r2} --aligner ${aligner} --output_file ${output_prefix} --threads ${threads} --local

# mkdir -p txt_out
# cp ./${output_prefix}.allele_mapping_data.txt ./txt_out/
# cp ./${output_prefix}.gene_mapping_data.txt ./txt_out/

