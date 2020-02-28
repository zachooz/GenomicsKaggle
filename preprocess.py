import argparse
import pprint

import numpy as np
import torch
from torch.utils.data import Dataset
import pickle


class HistoneDataset(Dataset):
    def __init__(self, input_file, save_path=None, load_path=None, mode="train"):
        """
        :param input_file: the data file pathname
        """
        self.pp = pprint.PrettyPrinter(indent=4)
        # TODO: read the input file line by line and put the lines in a list.
        npzfile = np.load(input_file)

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

        if load_path is not None:
            input = np.load(load_path[0] + "/" + mode + "/x.npy")
            output = np.load(load_path[0] + "/" + mode + "/y.npy")
            ids = np.load(load_path[0] + "/" + mode + "/id.npy")
            type = np.load(load_path[0] + "/" + mode + "/type.npy")
        else:
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

            if save_path is not None:
                np.save(save_path[0] + "/" + mode + "/x", input)
                np.save(save_path[0] + "/" + mode + "/y", output)
                np.save(save_path[0] + "/" + mode + "/id", ids)
                np.save(save_path[0] + "/" + mode + "/type", type)

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

        # height corresponds to rows
        self.height = self.x[0].size()[0]

        # print('width', self.width)
        # print('height', self.height)
        #
        # pp.pprint(npzfile[self.cell_types[0]][1])
        # pp.pprint(self.x[1])
        # print('id', self.id[1])
        # print('id', self.type[1])
        # print(len(self.type))
        # print(len(self.id))



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
            "x": self.x[idx],
            "y": self.y[idx],
            "width": self.width,
            "height": self.height
        }
        return item


if __name__ == '__main__':

    pp = pprint.PrettyPrinter(indent=4)
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input dataset')
    args = parser.parse_args()

    dataset = HistoneDataset(args.input_file)
    pp.pprint(dataset)
