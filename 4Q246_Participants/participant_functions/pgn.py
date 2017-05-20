from __main__ import * # this module assumes the Text-Fabric methods have been globalized

def get_pgn(word, pronom=False):
    '''
    Return a person, gender, number (PGN) tuple 
    for a word or pronominal suffix.
    '''
    # return word PGN tuple
    if not pronom:
        return (F.ps.v(word), F.gn.v(word), F.nu.v(word))
    
    # return pronominal suffix PGN tuple
    else:
        return (F.prs_ps.v(word), F.prs_gn.v(word), F.prs_nu.v(word))
    
    
def match_pgn(main_pgn, cmp_pgn):
    '''
    Return True/False for person, gender, and number agreement between:
        * a third person pronominal suffix and verbs
        OR
        * a third person pronominal suffix and nouns
    Requires two tuples formatted as: (person, gender, number)
        for the pronominal PGN and the compared PGN (verb or noun)
    '''
    # label pgn data
    main_ps, main_gn, main_nu = main_pgn
    cmp_ps, cmp_gn, cmp_nu = cmp_pgn
    
    # check the parameters for p3 subject/verb agreement
    if all([main_ps in {'p3','unknown','NA'},
            cmp_ps in {'p3','unknown','NA'},
            main_nu == cmp_nu,
            main_gn in {cmp_gn, 'unknown'} or cmp_gn == 'unknown']):
        
        return True
    
    else:
        return False