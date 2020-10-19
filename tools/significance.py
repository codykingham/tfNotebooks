'''
This module contains scripts for testing statistical associations.
'''

import collections
import numpy as np
import pandas as pd
import scipy.stats as stats

def normalize_axes(df, sample_axis, feature_axis):
    """Tests and transposes DataFrame to sample * feature format.
    
    Checks to make sure a user's axes inputs are 
    properly formatted. Flips a DF to put samples in
    index and features in columns.

    Arguments:
        df: dataset
        sample_axis: axis containing samples (0, 1)
        feature_axis: axis containing features (0,1)

    Returns: 
        DataFrame as samples * features
    
    """
    if sample_axis == 1 and feature_axis == 0:
        df = df.T
    elif sample_axis != 0 and feature_axis != 1:
        raise Exception('Invalid axis! Should be 0 or 1')
    return df

def contingency_table(df, sample_axis, feature_axis):
    """Build 2x2 contingency table for calculating association measures.

    A 2x2 contingency table is defined as:
    ----------------------------------
   |              feature     ¬feature |
   |  sample         A            B    |
   |  ¬sample        C            D    |
    -----------------------------------
    
    Where sample is, e.g., a given word  and feature 
    is a given co-occurrence construction (Levshina 2015, 224); 
    ¬sample  (i.e. "not" sample) is every sample besides 
    a given word and ¬feature is every feature besides a 
    given feature. "A", "B", "C", "D" are the frequency 
    integers between the given categories. I follow Levshina's 
    2015 explanation (224) on setting up 2x2 contingency tables 
    for testing collocations of linguistic constructions.  

    This method calculates A, B, C, D and "expected frequency"
    for a supplied dataset. The values are built into matrices
    of the same dimensions as the input matrix, so that for co-
    occurrence of sample*feature, one can access, e.g., the A
    or B value for that individual example, e.g.:

        >> df_b[wordX][featureY] = B value for wordX*featureY 
    
    Given a sample and a feature count in a dataset, the math 
    for finding A, B, C, D (see Levshina 2015, 223) is:

        >> A = frequency of sample w/ feature (in dataset)
        >> B = sum(sample) - A
        >> C = sum(feature) - A
        >> D = sum(dataset) - (A+B+C)

    And the expected frequency (ibid., 211) is:

        >> E = sum(sample) * sum(feature) / sum(dataset)

    Arguments:
        df: a dataframe with co-occurrence frequencies in shape
            of samples*features or feature*samples
        sample_axis: 0 (row) or 1 (column); axis that contains 
            the sample population
        feature_axis: 0 (row) or 1 (column); axis that contains
            the collocating features on samples

    Returns: 
        5-tuple of dataframes as (a, b, c, d, e)
    """    

    # put data in sample * feature format for calculations
    # will flip it back at end if needed
    df = normalize_axes(df, sample_axis, feature_axis)

    # get observation sums across samples / features
    # fill each row in a column with the sum across the whole column
    # and do same for columns
    samp_margins = df.apply(
        lambda row: row.sum(), 
        axis=1, 
        result_type='broadcast' # keeps same shape
    ) 
    feat_margins = df.apply(
        lambda col: col.sum(), 
        axis=0, 
        result_type='broadcast'
    ) 
    total_margin = df.sum().sum()
    b = samp_margins.sub(df) # NB "df" == a
    c = feat_margins.sub(df)
    # for d, make table where every cell is total margin
    # use that table to make subtractions:
    d = pd.DataFrame.copy(df, deep=True)
    d[:] = total_margin 
    d = d.sub(df+b+c)
    e = samp_margins * feat_margins / total_margin
    # flip axes back if needed:
    if sample_axis == 1:
        df,b,c,d,e = df.T, b.T, c.T, d.T, e.T
    return (df, b, c, d, e)
    
def apply_fishers(df, sample_axis, feature_axis, 
                 logtransform=True, sign=True):
    """Calculate Fisher's Exact Test with optional log10 transform.

    This function applies Fisher's Exact test to every 
    value in a co-occurrence matrix. It includes default 
    option to log-transform the results based on log10 
    and expected frequency condition. This is based on 
    the method of Stefanowitsch and Gries 2003, "Collostructions". 
    The resulting values "range from - infinitity (mutual repulsion) 
    to + infinity (mutual attraction)" (Levshina 2015, 232). 

    Arguments:
        df: a dataframe with co-occurrence frequencies in shape
            of samples*features or feature*samples
        sample_axis: 0 (row) or 1 (column); axis that contains 
            the sample population
        feature_axis: 0 (row) or 1 (column); axis that contains
            the collocating features on samples

    Returns:
        2-tuple of (p-values, odds_ratios) in DataFrames
    """

    # put data in sample * feature format for calculations
    # will flip it back at end if needed
    df = normalize_axes(df, sample_axis, feature_axis)
    a_df, b_df, c_df, d_df, e_df = contingency_table(df, 0, 1)
    ps = collections.defaultdict(lambda: collections.defaultdict())
    odds = collections.defaultdict(lambda: collections.defaultdict())

    # Calculate Fisher's value-by-value
    # I'm not yet sure if there's a better way to do this
    for sample in df.index:
        for feature in df.columns: 

            # exctract contingencies 
            a = df[feature][sample]
            b = b_df[feature][sample]
            c = c_df[feature][sample]
            d = d_df[feature][sample]
            expected_freq = e_df[feature][sample]

            # run Fisher's
            contingency = np.matrix([[a, b], [c, d]])
            oddsratio, p_value = stats.fisher_exact(contingency)
            
            # save and transform? scores
            odds[feature][sample] = oddsratio
            if not logtransform:
                if not sign:
                    ps[feature][sample] = p_value

                # apply signs
                else:
                    if a < expected_freq:
                        ps[feature][sample] = -p_value
                    else:
                        ps[feature][sample] = p_value

            # apply logtransform 
            else:
                if a < expected_freq:
                    with np.errstate(divide='ignore'):
                        strength = np.log10(p_value) # NB: log of decimal is negative
                else:
                    with np.errstate(divide='ignore'):
                        strength = -np.log10(p_value) # NB: *-1 makes negative result positive
                ps[feature][sample] = strength

    # package into dfs, flip axis back if needed
    orient = 'columns' if sample_axis == 0 else 'index' 
    ps = pd.DataFrame.from_dict(ps, orient=orient)
    odds = pd.DataFrame.from_dict(odds, orient=orient)
    return (ps, odds)

def apply_deltaP(df, sample_axis, feature_axis):
    """Apply ΔP unidirectional association measure to table.

    ΔP is a unidirectional association measure used in 
    pyscholinguistic research to model linguistic cues
    and their respective responses (Nick Ellis, "Language
    Acquisition as Rational Contingency Learning", 2006.). 
    The approach is modeled on a theory of associative learning 
    and language use, by which certain constructions "cue" 
    or prompt the brain to probabilistically retrieve 
    another construction. 

    ΔP is contingency-based. Given the normal contingency 
    data of a, b, c, d, ΔP can be calculated. Mathematically 
    ΔP can be represented as (Ellis 2006:11):

        >>  a/(a+b) - c/(c+d)

    This represents the probability of an observed collocation
    (C) given a target construction (CX) minus the probability 
    of the observed collocation without the target construction 
    (adapted from Ellis 2006: 11):

        >>  P(C|CX) - P(C|-CX) 

    In this function, the sample_axis is treated as the cue
    and the feature_axis as the response.

    Arguments:
        df: a dataframe with co-occurrence frequencies in shape
            of samples*features or feature*samples
        sample_axis: 0 (row) or 1 (column); axis that contains 
            the sample population
        feature_axis: 0 (row) or 1 (column); axis that contains
            the collocating features on samples
    """
    
    # get contingency data and calculate ΔP
    a,b,c,d,e = contingency_table(df, sample_axis, feature_axis)
    delta_p = a/(a+b) - c/(c+d)
    return delta_p
