# fern  flower  fortress  horns  leaves  orchids  room  trex
dataset="room"
W=504
H=378
accelerator="dp"
downscale=2
batch_size=32
option="baseline"

data_root='/data/csj000714/data'

python train_refine.py --name llff-refine-$dataset-${option} --accelerator $accelerator \
    --dataset_mode llff_refine --dataset_root ${data_root}/nerf_llff_data/${dataset} \
    --checkpoints_dir ./checkpoints/nerf-sr-refine --summary_dir ./logs/nerf-sr-refine \
    --img_wh $W $H --batch_size $batch_size \
    --n_epochs 100 --n_epochs_decay 0 \
    --print_freq 1000 --vis_freq 1000 --val_freq 1000 --save_epoch_freq 1 --val_epoch_freq 1 \
    --model refine \
    --lr_policy exp --lr 5e-4 --lr_final 5e-6 \
    --syn_dataroot ./checkpoints/nerf-sr/llff-${dataset}-${option}/30_val_vis \
    --refine_with_l1 --network_codebook 
