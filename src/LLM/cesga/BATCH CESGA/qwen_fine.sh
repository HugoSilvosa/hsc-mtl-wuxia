#!/bin/bash

#SBATCH --job-name=hscqwen_fine

#SBATCH --output=/mnt/netapp2/Store_uni/home/ulc/co/hsc/logs/qwen_fine_%j.o
#SBATCH --error=/mnt/netapp2/Store_uni/home/ulc/co/hsc/logs/qwen_fine_%j.e

#SBATCH -t 15:30:00
#SBATCH --gres=gpu:a100:2
#SBATCH -c 64
#SBATCH --mem-per-cpu=3G 

#SBATCH --mail-user=hugo.silvosa.cuervo@udc.es
#SBATCH --mail-type=ALL


module load cesga/system miniconda3/22.11.1-1
conda activate $STORE/entornos/tfgtest



export CUDA_LAUNCH_BLOCKING=1
export WANDB_MODE="disabled"
export HUGGING_FACE_HUB_TOKEN=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

export HUGGINGFACE_HUB_CACHE="/mnt/netapp2/Store_uni/home/ulc/co/hsc/cacheh"


TQDM_DISABLE=1 python $HOME/tfg/scripts/qwen_train.py --prompts 0 
