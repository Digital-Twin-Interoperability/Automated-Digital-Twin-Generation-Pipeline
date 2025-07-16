# CAD-Coder

[Paper](https://arxiv.org/abs/2505.14646) | [Dataset](https://github.com/anniedoris/GenCAD-Code) | Project Page (Coming soon!)

## Release Todo List

- [x] Release GenCADCode Dataset
- [ ] Release CAD-Coder and variants on HF
- [ ] Release Training Code

## Overview
**CAD-Coder generates CAD code (CadQuery Python) given an image input! Our model is a fine-tuned, open-source vision-langauge foundation model.** 

On a test-set of CAD images, we demonstrate that CAD-Coder out-performs state-of-the-art closed-source and open-source code-generating VLMs both in terms of valid syntax rate of output Python scripts and generated solid accuracy.

![CAD-Coder Results](docs_images/results.png)

## Dataset
To download our GenCAD-Code dataset, consisting of 163k image-CadQuery Python script pairs, follow the instructions on our corresponding [GenCAD-Code dataset repo](https://github.com/anniedoris/GenCAD-Code).

## Paper
Our paper was accepted to IDETC 2025! Check out our pre-print [here](https://arxiv.org/abs/2505.14646).

## Training CAD-Coder
### Environment Setup

1. Follow LLaVA environemnt setup steps
```
conda create -n llava python=3.10 -y
conda activate llava
pip install --upgrade pip  # enable PEP 660 support
pip install -e .
pip install -e ".[train]"
pip install datasets
pip install peft==0.10.0
pip install tensorboard
```

2. Install flash-attn
```
pip install flash-attn --no-build-isolation
```
Note: this did not work for me (although it is what is suggested in LLaVA setup steps). I instead had to download the relevant wheel file ```flash_attn-2.7.2.post1+cu12torch2.1cxx11abiFALSE-cp310-cp310-linux_x86_64.whl``` from [this](https://github.com/Dao-AILab/flash-attention/releases) website. Use the one relevant to your specific cuda/torch/architecture.

### Phase 1 Training

1. Identify a location that is good to store a large quantity of data (~30GB) and export its absolute path as an environment variable:
```
export CADCODER_DATA_ROOT = {/path_to_data_storage/goes_here}
```

2. Download the pre-training dataset. This is the same dataset that is used by LLaVA 1.5.
```
cd $CADCODER_DATA_ROOT
mkdir llava_pretrain_data
huggingface-cli download liuhaotian/LLaVA-Pretrain --repo-type=dataset --local-dir "${LLAVA_DATA_ROOT}/llava_pretrain_data"
cd llava_pretrain_data
unzip images.zip
```

3. Run the phase 1 training script:
```
./scripts/v1_5/pretrain.sh {your_checkpoint_save_root}
```

The phase1 trained model will be saved to {your_checkpoint_save_root}/phase1_cadcoder. We used 4 H100 GPUs for this phase of training, and it took 4.5 hours. During training of the model, you can check that the training loss looks something like what we got (see below) by running the following command:

```
cd {your_checkpoint_save_root}/phase1_cadcoder
tensorboard --logdir=runs
```

![CAD-Coder Phase 1 Training](docs_images/pretrain_results.png)

### Phase 2 Training
