'''
This module contains scripts for testing statistical associations.
'''

import collections
import numpy as np
import pandas as pd
import scipy.stats as stats
from datetime import datetime

np.seterr(divide='ignore')

def contingency_table(df):
    
    '''
    This function takes in a table
    of co-occurrence data and returns the 
    data necessary for 2x2 contingency tables
    for all elements.
    '''
    # pre-process data for contingency tables
    target_obs = df.apply(lambda col: col.sum(), axis=0, result_type='broadcast') # all columns filled with col sums
    colex_obs = df.apply(lambda row: row.sum(), axis=1, result_type='broadcast') # all rows filled with row sums
    total_obs = df.sum().sum() # total observations
    b_matrix = target_obs.sub(df)
    c_matrix = colex_obs.sub(df)
    d_matrix = pd.DataFrame.copy(df, deep=True)
    d_matrix[:] = total_obs # fill all cells with same number: the sum of all values in df
    d_matrix = d_matrix.sub(df+b_matrix+c_matrix)
    expected = (df+b_matrix) * (df+c_matrix) / (df+b_matrix+c_matrix+d_matrix)
    return {'a':df, 'b':b_matrix, 'c':c_matrix, 'd':d_matrix, 'expected':expected}
    
def apply_fishers(df, logtransform=True):
    '''
    This function simply applies Fisher's
    exact test to every value in a co-occurrence
    matrix. It returns a transformed matrix.
    Includes default option to log-transform
    the results based on log10 and expected
    frequency condition.
    '''
    
    i = 0 # counter for messages
    start = datetime.now()
    
    print(f'{datetime.now()-start}\t applying Fisher\'s to dataset')
    
    con = contingency_table(df)
    b_matrix, c_matrix, d_matrix, expected = [con[x] for x in ('b', 'c', 'd', 'expected')]
    dfsum = df.sum().sum() 
    
    niters = df.shape[0] * df.shape[1] # number of iterations
    
    dffishers = collections.defaultdict(lambda: collections.defaultdict())
    for target in df.columns:
        for colex in df.index: 
            # values for contingency table and expected freq.
            a = df[target][colex]
            b = b_matrix[target][colex]
            c = c_matrix[target][colex]
            d = dfsum - (a+b+c)
            
            # Fisher's
            contingency = np.matrix([[a, b], [c, d]])
            oddsratio, p_value = stats.fisher_exact(contingency)
            
            if not logtransform:
                dffishers[target][colex] = p_value
            else:
                expected_freq = expected[target][colex]
                if a < expected_freq:
                    strength = np.log10(p_value)
                else:
                    strength = -np.log10(p_value)
                dffishers[target][colex] = strength
                
            i += 1
            if i % 1000000 == 0: # update message every 1,000,000 iterations
                print(f'\t{datetime.now()-start}\t finished iteration {i}\t ({round((i/niters),2)*100})')
                
    print(f'{datetime.now()-start}\t DONE!')
                
    return pd.DataFrame(dffishers)