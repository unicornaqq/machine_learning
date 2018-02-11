#in this function, we are going to use the clustering method to cluster all the elements on the path to the hostconfcli.txt.
# 1. we use the scandir walk to list all the path that pointed to the hostconfcli.txt
# 2. we use 3 times of clustering to gain a beautiful clustering.
# 3. For the 1st time clustering, we try to limited the number of clusters as mush as possible
#    The 2nd time clustering, we try to cluster against each clustering, that means more candidate pattern will be added to the list
#    The 3nd time clustering, we just do cluster against all the examplers, and please note, we will ignore the short strings
#    since they will cause impact to the algorithm. We use the diff between the string as the distance, but if the string itself is short,
#    we can't tell if it is caused by the length of the string, or it is caused by the similarity between the 2 strings.
from scandir import scandir, walk
from multiprocessing import Pool

import fnmatch
import os
import itertools

import numpy as np
import sklearn.cluster
import distance

import pickle

def find_hostconfcli(start_point, temp_list=[]):
    for root, dirnames, filenames in walk(start_point):
        for file in filenames:
            if fnmatch.fnmatch(file, "hostconfcli*"):
                print root.split('/')
                temp_list.extend(root.split('/')[1:])
                #return os.path.join(root, file)
    return temp_list



def clustering(input_list, input_pref=0):
    words = np.asarray(input_list)
    #print words
    lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])
    min_lev = lev_similarity[lev_similarity != 0].min()
    print min_lev
    print lev_similarity[lev_similarity != 0].max()
    median_lev = np.median(lev_similarity)

    if input_pref != 0:
        median_lev = input_pref

    temp_list = list()

    affprop = sklearn.cluster.AffinityPropagation(preference=median_lev, affinity="precomputed", damping=0.8)
    affprop.fit(lev_similarity)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
        temp_list.append(exemplar)
        cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
        cluster_str = "\n ".join(cluster)
        print(" - *%s:* \n%s" % (exemplar, cluster_str))

    return temp_list

def two_level_clustering(input_list):
    words = np.asarray(input_list)
    #print words
    lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])
    min_lev = lev_similarity[lev_similarity != 0].min()
    print min_lev
    print lev_similarity[lev_similarity != 0].max()
    print np.median(lev_similarity)

    temp_list = list()

    affprop = sklearn.cluster.AffinityPropagation(preference=-200, affinity="precomputed", damping=0.8)
    affprop.fit(lev_similarity)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
        cluster_str = "\n ".join(cluster)
        print(" - *%s:* \n%s" % (exemplar, cluster_str))


        if cluster.size > 1:
            print "\n"
            print "clustering against the examplar", exemplar
            print len(exemplar)
            temp_list.append(exemplar)
            min_len = -1 * len(min(cluster, key=len))
            max_len = -1 * len(max(cluster, key=len))

            print "min_len is", min_len
            print "max_len is", max_len
            temp_list.extend(clustering(cluster, min_len))
            print "\n"

    return temp_list


if __name__ == "__main__":
    mypath = os.path.dirname(os.path.abspath(__file__))

    if os.path.isfile(mypath+'/result_dump.txt'):
        with open(mypath+'/result_dump.txt', 'rb') as f:
            unique_result = pickle.load(f)
    else:
        pool = Pool(40)
        results = pool.map(find_hostconfcli, os.listdir("./"), chunksize=5)
        unique_result = list(set(itertools.chain.from_iterable([x for x in results if x is not None])))
        with open(mypath+'/result_dump.txt', 'wb') as f:
            pickle.dump(unique_result, f)


    #print "two times clustering\n" 
    #examplar_list = clustering(unique_result)
    #second_level_examplar_list = clustering(examplar_list)

    print "two_level_clustering\n"
    final_exampler_list = two_level_clustering(unique_result)
    print "the final exampler list is \n"

    print final_exampler_list

    print "try to wash the list for the 3rd time based on the final exampler list\n"
    temp_list = [x for x in final_exampler_list if len(x) < 20]
    temp_list.extend(clustering([x for x in final_exampler_list if len(x) >= 20]))
    print temp_list
