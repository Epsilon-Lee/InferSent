# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree. 
#

import argparse
import sys, os
import logging

import numpy as np
import torch

from xutils import dotdict


GLOVE_PATH = "../dataset/GloVe/glove.840B.300d.txt"
PATH_SENTEVAL = "/home/aconneau/notebooks/SentEval/"
PATH_TRANSFER_TASKS = "/home/aconneau/notebooks/SentEval/data/senteval_data/"

assert os.path.isfile(GLOVE_PATH) and PATH_SENTEVAL and PATH_TRANSFER_TASKS, 'Set PATHs'

parser = argparse.ArgumentParser(description='NLI training')
parser.add_argument("--modelpath", type=str, default='infersent.allnli.pickle', help="path to model")
parser.add_argument("--gpu_id", type=int, default=0, help="GPU ID")
params, _ = parser.parse_known_args()


# import senteval
sys.path.insert(0, PATH_SENTEVAL)
import senteval    
    
# set gpu device
torch.cuda.set_device(params.gpu_id)

def prepare(params, samples):
    params.infersent.build_vocab([' '.join(s) for s in samples], tokenize=False)  
    
def batcher(batch, params):
    # batch contains list of words
    sentences = [' '.join(s) for s in batch]
    embeddings = params.infersent.encode(sentences, bsize=params.batch_size, tokenize=False)
    return embeddings


"""
Evaluation of trained model on Transfer Tasks (SentEval)
"""

# define transfer tasks
transfer_tasks = ['MR', 'CR', 'SUBJ', 'MPQA', 'SST', 'TREC', 'SICKRelatedness',\
                  'SICKEntailment', 'MRPC', 'STS14']

# define senteval params
params_senteval = dotdict({'usepytorch': True,
                           'task_path': PATH_TRANSFER_TASKS,
                           'seed': 1111,
                           })
# Set up logger
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

if __name__ == "__main__":
    # Load model
    params_senteval.infersent = torch.load(params.modelpath)
    params_senteval.infersent.set_glove_path(GLOVE_PATH)

    se = senteval.SentEval(batcher, prepare, params_senteval)
    results_transfer = se.eval(transfer_tasks)

    print(results_transfer)

