import os.path as osp
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_cluster import random_walk
import pandas as pd
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
from torch_geometric.loader import NeighborSampler as RawNeighborSampler
%matplotlib inline
import matplotlib.pyplot as plt
import numpy
from sklearn.manifold import TSNE

EPS = 1e-15

# Reads in csv file and get rid of unnesscary columnn in the data frame
dataFrame = pd.read_csv(sys.argv[1])
dataFrame.pop('Unnamed: 0')

# Creates a list of indices between each of the edges that wiill go into a
# graph that will be fed into a GNN, which in this case represents the link
# between the methods and the methods that are called
edgeIndex = torch.tensor([dataFrame['called_index'], dataFrame['callee_index']], dtype=torch.long)

# Creates a list of random X values and makes sure that list is big enough
# to provide a value for every node that exists between the edges in the edgeIndex
maxCalledIndex = dataFrame['called_index'].max()
maxCalleeIndex = dataFrame['callee_index'].max()
maxIndex = max(maxCalledIndex, maxCalleeIndex)
additionalXValues = maxIndex + 1 - dataFrame.shape[0]
x = torch.rand(dataFrame.shape[0]+additionalXValues, dataFrame.shape[0], dtype=torch.float)

# Creates a graph of the csv data frame that can be fed intoo the GNN
data = Data(x=x, edge_index=edgeIndex.t().contiguous())


# Visualizes the learned features of the nodes using
# t-SNE generated graphs
def visualize(h, color):
    z = TSNE(n_components=2).fit_transform(h.detach().cpu().numpy())
    plt.figure(figsize=(10,10))
    plt.xticks([])
    plt.yticks([])

    plt.scatter(z[:, 0], z[:, 1], s=70, c=color, cmap="Set2")
    plt.show()

# This class outputs node embeddings for each node in the graph
# that are dependent upon the neighborhood that the node is in
# instead of looking at every node individually
class NeighborSampler(RawNeighborSampler):
    def sample(self, batch):
        batch = torch.tensor(batch)
        row, col, _ = self.adj_t.coo()

        # For each node in `batch`, we sample a direct neighbor (as positive
        # example) and a random node (as negative example):
        pos_batch = random_walk(row, col, batch, walk_length=1,
                                coalesced=False)[:, 1]

        neg_batch = torch.randint(0, self.adj_t.size(1), (batch.numel(), ),
                                  dtype=torch.long)

        batch = torch.cat([batch, pos_batch, neg_batch], dim=0)
        return super(NeighborSampler, self).sample(batch)


# Calls the NeighborSamples class to get node embeddings
train_loader = NeighborSampler(data.edge_index, sizes=[10, 10], batch_size=256,
                               shuffle=True, num_nodes=data.num_nodes)


# This class is the actual GNN model that is being
# used and it trains on the input data and learns
# how to predict links between the nodes
class SAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels, num_layers):
        super(SAGE, self).__init__()
        self.num_layers = num_layers
        self.convs = nn.ModuleList()
        for i in range(num_layers):
            in_channels = in_channels if i == 0 else hidden_channels
            self.convs.append(SAGEConv(in_channels, hidden_channels))

    def forward(self, x, adjs):
        for i, (edge_index, _, size) in enumerate(adjs):
            x_target = x[:size[1]]  # Target nodes are always placed first.
            x = self.convs[i]((x, x_target), edge_index)
            if i != self.num_layers - 1:
                x = x.relu()
                x = F.dropout(x, p=0.5, training=self.training)
        return x

    def full_forward(self, x, edge_index):
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i != self.num_layers - 1:
                x = x.relu()
                x = F.dropout(x, p=0.5, training=self.training)
        return x


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SAGE(data.num_node_features, hidden_channels=64, num_layers=2)
model = model.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
x, edge_index = data.x.to(device), data.edge_index.to(device)


# Trains the GNN with the training data from the
# train_loader and returns the total amount of loss, or
# the prediction error of the GNN
def train():
    model.train()

    total_loss = 0
    for batch_size, n_id, adjs in train_loader:
        # `adjs` holds a list of `(edge_index, e_id, size)` tuples.
        adjs = [adj.to(device) for adj in adjs]
        optimizer.zero_grad()

        out = model(x[n_id], adjs)
        out, pos_out, neg_out = out.split(out.size(0) // 3, dim=0)

        pos_loss = F.logsigmoid((out * pos_out).sum(-1)).mean()
        neg_loss = F.logsigmoid(-(out * neg_out).sum(-1)).mean()
        loss = -pos_loss - neg_loss
        loss.backward()
        optimizer.step()

        total_loss += float(loss) * out.size(0)

    return total_loss / data.num_nodes


# Runs the data through the train function one hundred
# times, printing out the loss for each epoch, and
# creates a t-SNE graph to visualize the results after every 10 epochs
for epoch in range(1, 101):
    loss = train()
    print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}, ')
    if epoch % 10 == 0:
      out = model.full_forward(x, edgeIndex).cpu()
      visualize(out, 'blue')
