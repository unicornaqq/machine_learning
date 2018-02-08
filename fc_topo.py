# Use the built-in version of scandir/walk if possible, otherwise
# use the scandir module version
from scandir import scandir, walk
from multiprocessing import Pool

import fnmatch
import os
import itertools

import numpy as np
import sklearn.cluster
import distance



def find_hostconfcli(start_point):
    for root, dirnames, filenames in walk(start_point):
        for file in filenames:
            if fnmatch.fnmatch(file, "hostconfcli*"):
                #print root.split('/')
                return root.split('/')[1:]
                #return os.path.join(root, file)


def find_hostconfcli2(start_point):
    for directory in os.listdir(start_point):
        if os.path.isdir(os.path.join(start_point, directory)):
            if any(fnmatch.fnmatch(directory, pattern) for pattern in ["execu*", "TestCases*", "*data_collection*","*auto_triage__*", "spa", "cmd_output*", "*service_data*", "OB-*", "CCT_*", "201[0-9]-*", "triage__*"]):
                #print directory
                if fnmatch.fnmatch(directory, "cmd_output*"):
                    for filename in os.listdir(os.path.join(start_point, directory)):
                        if fnmatch.fnmatch(filename, "hostconfcli*"):
                            return os.path.join(start_point, directory, filename)
                else:
                    find_hostconfcli2(os.path.join(start_point, directory))

def clustering(input_list):
    words = np.asarray(input_list)
    print words
    lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])
    print lev_similarity[lev_similarity != 0].min()
    print lev_similarity[lev_similarity != 0].max()
    print np.median(lev_similarity)

    temp_list = list()

    affprop = sklearn.cluster.AffinityPropagation(preference=-40, affinity="precomputed", damping=0.5)
    affprop.fit(lev_similarity)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]] 
        temp_list.append(exemplar)
        cluster = np.unique(words[np.nonzero(affprop.alabels_==cluster_id)])
        cluster_str = "\n ".join(cluster)
        print(" - *%s:* \n%s" % (exemplar, cluster_str))

    return temp_list

if __name__ == "__main__":
    pool = Pool(40)
    results = pool.map(find_hostconfcli, os.listdir("./"), chunksize=5)
    unique_result = list(set(itertools.chain.from_iterable([x for x in results if x is not None])))
    
    examplar_list = clustering(unique_result)
    
    second_level_examplar_list = clustering(examplar_list)

    
