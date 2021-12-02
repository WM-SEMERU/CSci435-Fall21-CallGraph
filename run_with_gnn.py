import os.path as osp
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Linear
from torch_cluster import random_walk
from sklearn.linear_model import LogisticRegression
import pandas as pd
from torch_geometric.data import InMemoryDataset
from torch_geometric.data import Data
from sklearn.model_selection import train_test_split

import torch_geometric.transforms as T
from torch_geometric.nn import SAGEConv
from torch_geometric.datasets import Planetoid
from torch_geometric.loader import NeighborSampler as RawNeighborSampler

EPS = 1e-15

dataFrame = pd.read_csv('javaOutputTest2_edge.csv')
dataFrame.pop('Unnamed: 0')
print(dataFrame)

callLine = []
for val in dataFrame['call_line']:
  callLine.append([val])

edgeIndex = torch.tensor([dataFrame['called_index'], dataFrame['callee_index']], dtype=torch.long)
x = torch.tensor(callLine, dtype=torch.float)
y = torch.tensor(callLine, dtype=torch.float)

data = Data(x=x, edge_index=edgeIndex.t().contiguous(), y=y, val_mask=2, train_mask=2, test_mask=2)
data.num_nodes = dataFrame.shape[0]
data.num_classes = 1

print(data)
print(edgeIndex)

%matplotlib inline
import matplotlib.pyplot as plt
import numpy
from sklearn.manifold import TSNE

def visualize(h, color):
    print(h)
    z = TSNE(n_components=2).fit_transform(h.detach().cpu().numpy())
    print(z)
    plt.figure(figsize=(10,10))
    plt.xticks([])
    plt.yticks([])

    plt.scatter(z[:, 0], z[:, 1], s=70, c=color, cmap="Set2")
    plt.show()


class MLP(torch.nn.Module):
    def __init__(self, hidden_channels):
        super(MLP, self).__init__()
        torch.manual_seed(12345)
        self.lin1 = Linear(data.num_features, hidden_channels)
        self.lin2 = Linear(hidden_channels, data.num_classes)

    def forward(self, x):
        x = self.lin1(x)
        x = x.relu()
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.lin2(x)
        return x


# from IPython.display import Javascript  # Restrict height of output cell.
# display(Javascript('''google.colab.output.setIframeHeight(0, true, {maxHeight: 300})'''))

model = MLP(hidden_channels=16)
criterion = torch.nn.CrossEntropyLoss()  # Define loss criterion.
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)  # Define optimizer.

def train():
      model.train()
      optimizer.zero_grad()  # Clear gradients.
      out = model(data.x)  # Perform a single forward pass.
      loss = criterion(out, data.y)  # Compute the loss solely based on the training nodes.
      loss.backward()  # Derive gradients.
      optimizer.step()  # Update parameters based on gradients.
      return loss

def test():
      model.eval()
      out = model(data.x)
      pred = out.argmax(dim=1)  # Use the class with highest probability.
      test_correct = pred[data.test_mask] == data.y[data.test_mask]  # Check against ground-truth labels.
      test_acc = int(test_correct.sum()) / int(data.test_mask.sum())  # Derive ratio of correct predictions.
      return test_acc

for epoch in range(1, 201):
    loss = train()
    print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')

# test_acc = test()
# print(f'Test Accuracy: {test_acc:.4f}')

# out = model(data.x, data.edge_index)
# visualize(out, color=data.y)
