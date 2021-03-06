# coding=utf-8
"""
© 2016. Case Recommender All Rights Reserved (License GPL3)

User Based Collaborative Filtering Recommender

    User-kNN predicts a user’s rating according to how similar users rated the same item. The algorithm matches similar
    users based on the similarity of their ratings on items.


Parameters
-----------
    - train_file: string
    - test_file: string
    - ranking_file: string
        file to write final ranking
    - similarity_metric: string
        Pairwise metric to compute the similarity between the users.
        Reference about distances:
            - http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.distance.pdist.html
    - neighbors: int
        The number of user candidates strategy that you can choose for selecting the possible items to recommend.
    - rank_number int
        The number of items per user that appear in final rank
    - implicit bool
        If True define fill matrix with 0s and 1s

"""

import numpy as np
from scipy.spatial.distance import squareform, pdist
from framework.evaluation.item_recommendation import ItemRecommendationEvaluation
from framework.utils.extra_functions import timed
from framework.utils.read_file import ReadFile
from framework.utils.write_file import WriteFile

__author__ = "Arthur Fortes"


class UserKNN(object):
    def __init__(self, train_file, test_file=None, ranking_file=None, similarity_metric="correlation", neighbors=30,
                 rank_number=10, implicit=False):
        self.train_set = ReadFile(train_file).return_matrix(implicit)
        self.train = self.train_set["matrix"]
        self.test_file = test_file
        self.users = self.train_set["users"]
        self.items = self.train_set["items"]
        if self.test_file is not None:
            self.test_set = ReadFile(test_file).rating_prediction()
            self.users = sorted(set(self.train_set["users"] + self.test_set["users"]))
            self.items = sorted(set(self.train_set["items"] + self.test_set["items"]))
        self.k = neighbors
        self.similarity_metric = similarity_metric
        self.ranking_file = ranking_file
        self.rank_number = rank_number
        self.ranking = list()
        self.su_matrix = None
        self.matrix = self.train_set["matrix"]

    def compute_similarity(self):
        # Calculate distance matrix between users
        self.su_matrix = np.float32(squareform(pdist(self.matrix, self.similarity_metric)))
        # transform distances in similarities
        self.su_matrix = 1 - self.su_matrix
        del self.matrix

    def _predict_score(self, user_i, user_j):
        pass

    def predict(self):
        for user in range(len(self.train)):
            partial_ranking = list()
            u_list = list(np.flatnonzero(self.train[user] == 0))
            neighbors = sorted(list(range(len(self.su_matrix[user]))), key=lambda m: -self.su_matrix[user][m])

            for item in u_list:
                sim_suv = 0
                common_user_neighbor = list(set(self.train_set["di"][item]).intersection(set(neighbors[1:self.k])))

                if len(common_user_neighbor) > 0:
                    for user_neighbor in common_user_neighbor:
                        sim = 0 if np.math.isnan(self.su_matrix[user][user_neighbor]
                                                 ) else self.su_matrix[user][user_neighbor]
                        sim_suv += sim

                    partial_ranking.append((self.train_set["map_user"][user], self.train_set["map_item"][item],
                                            sim_suv))

            partial_ranking = sorted(partial_ranking, key=lambda x: -x[2])[:self.rank_number]
            self.ranking += partial_ranking

        if self.ranking_file is not None:
            WriteFile(self.ranking_file, self.ranking).write_ranking_file()

    def evaluate(self):
        result = ItemRecommendationEvaluation()
        res = result.test_env(self.ranking, self.test_file)
        print(("Eval:: Prec@1:" + str(res[0]) + " Prec@3:" + str(res[2]) + " Prec@5:" + str(res[4]) + " Prec@10:" +
              str(res[6]) + " Map::" + str(res[8])))

    def execute(self):
        print("[Case Recommender: Item Recommendation > UserKNN Algorithm]\n")
        print(("training data:: " + str(len(self.train_set["map_user"])) + " users and " + str(len(
            self.train_set["map_item"])) + " items and " + str(self.train_set["number_interactions"]) + " interactions"))
        if self.test_file is not None:
            test_set = ReadFile(self.test_file).return_matrix()
            print(("test data:: " + str(len(test_set["map_user"])) + " users and " + str(len(test_set["map_item"])) +
                  " items and " + str(test_set["number_interactions"]) + " interactions"))
            del test_set
        print(("training time:: " + str(timed(self.compute_similarity))) + " sec")
        print(("prediction_time:: " + str(timed(self.predict))) + " sec\n")
        if self.test_file is not None:
            self.evaluate()
