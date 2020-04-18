import os
import sys
import json

import numpy as np
import torch

from torch import nn, optim

from utils.Worker import Worker
from utils.Data_Prepper import Data_Prepper
from utils.Federated_Learner import Federated_Learner
from utils.models import LogisticRegression, MLP_LogReg, MLP_Net, CNN_Net

use_cuda = True


args = {
	# system parameters
	'device': torch.device("cuda" if torch.cuda.is_available() and use_cuda else "cpu"),
	# setting parameters
	'dataset': 'adult',
	'sample_size_cap': 5000,
	'n_workers': 5,
	'split': 'powerlaw', #classimbalance
	'theta': 0.1,  # privacy level -> at most (theta * num_of_parameters) updates
	'batch_size' : 16, # use this batch_size
	'train_val_split_ratio': 0.9,

	# model parameters
	'model_fn': LogisticRegression,
	'optimizer_fn': optim.SGD,
	'loss_fn': nn.CrossEntropyLoss(), 
	'lr': 0.001, # use this lr

	# training parameters
	'pretrain_epochs': 5,
	'fl_epochs': 100,
	'fl_individual_epochs': 5,
	'aggregate_mode':'credit-sum',  # 'mean', 'sum'

}


def run_experiments(args, repeat=1):
	# init steps
	print("Experimental settings are: ", args)
	
	performance_dicts = []
	for i in range(repeat):

		print("Experiment : No.{}/{}".format(str(i+1) ,str(repeat)))
		data_prep = Data_Prepper(args['dataset'], train_batch_size=args['batch_size'], sample_size_cap=args['sample_size_cap'], train_val_split_ratio=args['train_val_split_ratio'])
		
		federated_learner = Federated_Learner(args, data_prep)

		# train
		federated_learner.train()
		# analyze
		federated_learner.get_fairness_analysis()

		performance_dicts.append(federated_learner.performance_dict)
	
	keys = ['standalone_vs_final', 'standlone_vs_rrdssgd', 'sharingcontribution_vs_final',
			'rr_dssgd_avg', 'CFFL_best_worker', 'standalone_best_worker',
			# 'sharingcontribution_vs_improvements'
			 ]

	aggregate_dict = {}
	for key in keys:
		list_of_performance = [performance_dict[key] for performance_dict in performance_dicts]
		aggregate_dict[key] = np.array(list_of_performance).tolist()
		aggregate_dict[key +'_mean'] = np.mean(aggregate_dict[key], axis=0).tolist()
		aggregate_dict[key +'_std'] = np.std(aggregate_dict[key], axis=0).tolist()

		# print(key, aggregate_dict[key])
		print(key +'_mean', aggregate_dict[key +'_mean'])
		# print(key +'_std', aggregate_dict[key +'_std'])
	return



if __name__ == '__main__':
	# init steps
	
	n_workers, sample_size_cap, fl_epochs = [5, 2000, 100]
	theta = 0.1
	args['n_workers'] = n_workers
	args['sample_size_cap'] = sample_size_cap
	args['fl_epochs'] = fl_epochs
	args['theta'] = theta

	run_experiments(args, 3)