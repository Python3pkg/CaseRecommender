# coding=utf-8
"""
© 2016. Case Recommender All Rights Reserved (License GPL3)

k-fold cross-validation

    In k-fold cross-validation, the original sample is randomly partitioned into k equal sized subsamples.
    Of the k subsamples, a single subsample is retained as the validation data for testing the model, and the remaining
    k − 1 subsamples are used as training data. The cross-validation process is then repeated k times (the folds),
    with each of the k subsamples used exactly once as the validation data.

    The k results from the folds can then be averaged (or otherwise combined) to produce a single estimation.
    The advantage of this method over repeated random sub-sampling (see below) is that all observations are used for
     both training and validation, and each observation is used for validation exactly once. 10-fold cross-validation
     is commonly used, but in general k remains an unfixed parameter.

    When k=n (the number of observations), the k-fold cross-validation is exactly the leave-one-out cross-validation.

    In stratified k-fold cross-validation, the folds are selected so that the mean response value is approximately equal
    in all the folds. In the case of a dichotomous classification, this means that each fold contains roughly the
    same proportions of the two types of class labels.

    Literature:
        https://en.wikipedia.org/wiki/Cross-validation_(statistics)

Parameters
-----------
    - input_file: string
    - space_type: string
        TDivide data space type. E.g:
            '\t'  = tabular [default]
            ','   = comma
            '.'   = dot
    - dir_folds: string
        Directory to write the folds
    - n_folds: int
        Number to divide data in folds

"""

import random
from framework.utils.read_file import ReadFile
from framework.utils.write_file import WriteFile

__author__ = 'Arthur Fortes'


class CrossFoldValidation(object):
    def __init__(self, input_file, space_type='\t', dir_folds='', n_folds=10):
        self.dataset = input_file
        self.n_folds = n_folds
        self.space_type = space_type
        self.dict_folds = dict()

        self.divide_dataset()

        if dir_folds != '':
            WriteFile(dir_folds, self.dict_folds, self.space_type).cross_fold_validation()

    def divide_dataset(self):
        tp = ReadFile(self.dataset, space_type=self.space_type)
        tp.triple_information()
        random.shuffle(tp.triple_dataset)

        # Get the number of interactions that each partition should have.
        partition_size = int(float(tp.number_interactions) / float(self.n_folds))

        list_folds = list()
        last = -1

        for p in range(self.n_folds):
            initial = 1 + last
            final = (p + 1) * partition_size
            list_folds.append(tp.triple_dataset[initial:final])
            last = final

        for fold in range(self.n_folds):
            train_set = list()
            for fold_train in range(self.n_folds):
                if fold_train != fold:
                    train_set += list_folds[fold_train]
                train_set.sort()

            list_folds[fold].sort()
            self.dict_folds[fold] = {'train': train_set, 'test': list_folds[fold]}
