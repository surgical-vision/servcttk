import numpy as np


def describe_error_disparity(diff_vector, absolute=None, badn_error=[.5, 1, 2, 3, 4, 5]):

    metrics = describe_error_depth(diff_vector, absolute=absolute)
    
    abs_diff_vector = np.abs(diff_vector)
    metrics['EPE'] = np.mean(abs_diff_vector)
    for n in badn_error:
        metrics['Bad'+str(n)] = (np.sum(abs_diff_vector>n)/len(abs_diff_vector))*100
    return metrics
    



def describe_error_depth(diff_vector, absolute=None):
    metrics={}
    metrics['RMS'] = np.sqrt(np.sum((diff_vector)**2)/len(diff_vector))
    if (absolute is None) or (absolute == True):
        abs_diff_vector = np.abs(diff_vector)
        metrics['Mean (Absolute)'] = np.mean(abs_diff_vector)
        metrics['Median (Absolute)'] = np.median(abs_diff_vector)
        metrics['Std (Absolute)'] = np.std(abs_diff_vector)
        metrics['Max (Absolute)'] = np.amax(abs_diff_vector)
        metrics['Min (Absolute)'] = np.amin(abs_diff_vector)
        metrics['Q1 (Absolute)'] = np.percentile(abs_diff_vector,25)
        metrics['Q3 (Absolute)'] = np.percentile(abs_diff_vector,75)
    
    if (absolute is None) or (absolute == False):
        metrics['Mean'] = np.mean(diff_vector)
        metrics['Median'] = np.median(diff_vector)
        metrics['Std'] = np.std(diff_vector)
        metrics['Max'] = np.amax(diff_vector)
        metrics['Min'] = np.amin(diff_vector)
        metrics['Q1'] = np.percentile(diff_vector,25)
        metrics['Q3'] = np.percentile(diff_vector,75)
    return metrics
