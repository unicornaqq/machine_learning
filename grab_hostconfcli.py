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



def find_hostconfcli(start_point, temp_list=[]):
    for root, dirnames, filenames in walk(start_point):
        for file in filenames:
            if fnmatch.fnmatch(file, "hostconfcli*"):
                #print root.split('/')
                #return root.split('/')[1:]
                temp_list.append(os.path.join(root, file))
    return temp_list

def find_hostconfcli2(start_point, temp_list=[]):
    for directory in os.listdir(start_point):
        if os.path.isdir(os.path.join(start_point, directory)):
            if any(fnmatch.fnmatch(directory, pattern) for pattern in ["execu*", "TestCases*", "*data_collection*","*auto_triage__*", "spa", "spb", "cmd_output*", "*service_data*", "OB-*", "*CCT*", "*BBT*", "201[0-9]-*", "triage__*", "svc_dc", "testSet*", "safe_dump*"]):
                if fnmatch.fnmatch(directory, "cmd_output*"):
                    for filename in os.listdir(os.path.join(start_point, directory)):
                        if fnmatch.fnmatch(filename, "hostconfcli*"):
                            temp_list.append(os.path.join(start_point, directory,filename))
                else:
                    find_hostconfcli2(os.path.join(start_point, directory), temp_list)
    return temp_list



if __name__ == "__main__":

    #pool = Pool(163)
    #result_list = pool.map(find_hostconfcli2, os.listdir("./"))
    #unique_result = list(set(itertools.chain.from_iterable([x for x in result_list if x is not None])))
    #print unique_result
    #print len(unique_result)

    pool = Pool(163)
    result_list = pool.map(find_hostconfcli, os.listdir("./"))
    non_empty = list(set(itertools.chain.from_iterable([x for x in result_list if x is not None])))
    print non_empty
    print len(non_empty)

    #print set(unique_result).symmetric_difference(set(non_empty))
