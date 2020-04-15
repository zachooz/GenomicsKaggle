import argparse
import pprint

import numpy as np
import torch
from torch.utils.data import Dataset
import pandas as pd

class HistoneDataset(Dataset):
    def __init__(self, input_file, seq_file):
        """
        :param input_file: the data file pathname
        """
        self.id2seq = dict()
        self.pp = pprint.PrettyPrinter(indent=4)
        npzfile = np.load(input_file)
        seqs = pd.read_csv(seq_file, index_col=False, names=["id", "sequence"])
        for index, row in seqs.iterrows():
            self.id2seq[row['id']] = torch.tensor(self.onehot_encode(row['sequence'])).float()

        # [50, 16000, 100, 7]
        # [cell_types, genes, bins, (columns)]
        # columns = GeneID, H3K27me3, H3K36me3, H3K4me1, H3K4me3, H3K9me3, Expression Value (same for entire bin)
        # columns 0: GeneId, 1-5: Histone Marks, 6: Expression Value
        self.npdata = npzfile
        self.cell_types = npzfile.files

        # pp.pprint(npzfile[self.cell_types[0]][0])

        # [cell_types, genes, bins, histomes]
        input = []
        # [cell_types, genes, expression]
        output = []
        # [cell_types, genes, expression]
        ids = []
        # type
        type = []

        for cell in self.cell_types:
            cell_data = self.npdata[cell]
            id = cell_data[:, 0, 0]
            hm_data = cell_data[:, :, 1:6]
            exp_values = cell_data[:, 0, 6]
            ids.append(id)
            input.append(hm_data)
            output.append(exp_values)
            type.extend([cell] * cell_data.shape[0])

        # [cell_types*genes, bins, histomes]
        input = np.concatenate(input, axis=0)
        # [cell_types*genes, expression]
        output = np.concatenate(output, axis=0)
        ids = np.concatenate(ids, axis=0)
        type = np.asarray(type)

        self.x = []
        self.y = []
        self.id = ids
        self.type = type

        for x in input:
            self.x.append(torch.tensor(x))

        for y in output:
            self.y.append(torch.tensor(y))

        # width corresponds to columns
        self.width = self.x[0].size()[1]

        # height corresponds to rows - 100
        self.height = self.x[0].size()[0]

    def onehot_encode(self, sequence):
        molecule_to_vec = {
            'A': 0,
            'C': 1,
            'T': 2,
            'G': 3,
            'N': 4
        }
        onehot_matrix = np.zeros((len(sequence), 5))
        for i in range(len(sequence)):
            onehot_matrix[i][molecule_to_vec[sequence[i]]] = 1

        return onehot_matrix


    def __len__(self):
        """
        len should return a the length of the dataset

        :return: an integer length of the dataset
        """
        # TODO: Override method to return length of dataset
        return len(self.y)

    def __getitem__(self, idx):
        """
        getitem should return a tuple or dictionary of the data at some index
        In this case, you should return your original and target sentence and
        anything else you may need in training/validation/testing.

        :param idx: the index for retrieval

        :return: tuple or dictionary of the data
        """
        # TODO: Override method to return the items in dataset
        item = {
            "cell_type": self.type[idx],
            "id": self.id[idx],
            "x": torch.cat((self.x[idx], self.id2seq[self.id[idx]]), dim=0),
            "y": self.y[idx],
        }
        return item


if __name__ == '__main__':

    pp = pprint.PrettyPrinter(indent=4)
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input dataset')
    args = parser.parse_args()

    dataset = HistoneDataset(args.input_file)
    pp.pprint(dataset)
