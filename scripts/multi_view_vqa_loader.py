#!/usr/bin/env python3
"""
Multi-view VQA loader for CAD-Coder.
This script modifies the standard VQA loader to handle multiple images per question.
"""

import argparse
import torch
import os
import json
from tqdm import tqdm
import shortuuid

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import tokenizer_image_token, process_images, get_model_name_from_path

from PIL import Image
import math


def split_list(lst, n):
    """Split a list into n (roughly) equal-sized chunks"""
    chunk_size = math.ceil(len(lst) / n)  # integer division
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]


def get_chunk(lst, n, k):
    chunks = split_list(lst, n)
    return chunks[k]


def eval_model_multi_view(args):
    """Evaluate model with multi-view inputs."""
    # Model
    disable_torch_init()
    model_path = os.path.expanduser(args.model_path)
    model_name = get_model_name_from_path(model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, args.model_base, model_name)

    questions = [json.loads(q) for q in open(os.path.expanduser(args.question_file), "r")]
    questions = get_chunk(questions, args.num_chunks, args.chunk_idx)
    answers_file = os.path.expanduser(args.answers_file)
    os.makedirs(os.path.dirname(answers_file), exist_ok=True)
    ans_file = open(answers_file, "w")
    
    for line in tqdm(questions):
        idx = line["question_id"]
        qs = line["text"]
        cur_prompt = qs
        
        # Handle multi-view vs single view
        if "images" in line:
            # Multi-view: multiple images
            image_files = line["images"]
            print(f"Processing multi-view: {idx} with {len(image_files)} images")
        else:
            # Single view: one image
            image_files = [line["image"]]
            print(f"Processing single view: {idx}")
        
        # Build image tokens for all images
        image_tokens = ""
        images = []
        
        for image_file in image_files:
            if model.config.mm_use_im_start_end:
                image_tokens += DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n'
            else:
                image_tokens += DEFAULT_IMAGE_TOKEN + '\n'
            
            # Load image
            image = Image.open(os.path.join(args.image_folder, image_file)).convert('RGB')
            images.append(image)
        
        # Combine image tokens with question
        qs = image_tokens + qs

        conv = conv_templates[args.conv_mode].copy()
        conv.append_message(conv.roles[0], qs)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()

        # Process all images
        image_tensors = []
        image_sizes = []
        for image in images:
            image_tensor = process_images([image], image_processor, model.config)[0]
            image_tensors.append(image_tensor)
            image_sizes.append(image.size)
        
        # Stack images if multiple
        if len(image_tensors) > 1:
            image_tensor = torch.stack(image_tensors, dim=0)
        else:
            image_tensor = image_tensors[0].unsqueeze(0)

        with torch.inference_mode():
            output_ids = model.generate(
                input_ids,
                images=image_tensor.half().cuda(),
                image_sizes=image_sizes,
                do_sample=True if args.temperature > 0 else False,
                temperature=args.temperature,
                top_p=args.top_p,
                num_beams=args.num_beams,
                max_new_tokens=args.max_new_tokens,
                use_cache=True)

        outputs = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

        ans_id = shortuuid.uuid()
        ans_file.write(json.dumps({"question_id": idx,
                                   "prompt": cur_prompt,
                                   "text": outputs,
                                   "answer_id": ans_id,
                                   "model_id": model_name,
                                   "metadata": {}}) + "\n")
        ans_file.flush()
    ans_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="facebook/opt-350m")
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--image-folder", type=str, default="")
    parser.add_argument("--question-file", type=str, default="tables/question.jsonl")
    parser.add_argument("--answers-file", type=str, default="answer.jsonl")
    parser.add_argument("--conv-mode", type=str, default="llava_v1")
    parser.add_argument("--num-chunks", type=int, default=1)
    parser.add_argument("--chunk-idx", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--num_beams", type=int, default=1)
    parser.add_argument("--max_new_tokens", type=int, default=3450)
    args = parser.parse_args()

    eval_model_multi_view(args)






