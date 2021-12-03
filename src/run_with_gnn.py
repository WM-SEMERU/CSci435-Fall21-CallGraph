import os.path as osp
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_cluster import random_walk
from sklearn.linear_model import LogisticRegression
import pandas as pd
from torch_geometric.data import InMemoryDataset
from torch_geometric.data import Data

import torch_geometric.transforms as T
from torch_geometric.nn import SAGEConv
from torch_geometric.datasets import Planetoid
from torch_geometric.loader import NeighborSampler as RawNeighborSampler

EPS = 1e-15

dataFrame = pd.read_csv(sys.argv[1])
dataFrame.pop('Unnamed: 0')
print(dataFrame)

x = [dataFrame.shape[0], len(dataFrame['callee_index'].unique())]
print(x)

edgeIndex = torch.tensor([dataFrame['called_index'], dataFrame['callee_index']], dtype=torch.long)
x = torch.tensor(dataFrame['call_line'], dtype=torch.long)
data = Data(x=x, edge_index=edgeIndex.t().contiguous(), y=x, val_mask=x, train_mask=x, test_mask=x)
print(data)
data.num_nodes = dataFrame.shape[0]
print(data.num_nodes)
