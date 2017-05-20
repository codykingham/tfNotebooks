from __main__ import * # this module assumes the Text-Fabric methods have been globalized

def is_preposition_subj(word):
    '''
    Return boolean on whether a word is a preposition subject,
    necessary for cases in which the subject is marked in
    a prepositional phrase, such as in passive clauses.
    Require a word node.
    
    *Caution*
    Does not capture cases such as Gen 21:5 (ca# 516487)
    '''
    # get word phrase
    w_phrase = L.u(word, otype='phrase')[0]
    
    # return false if wordnode not in a subject phrase
    if F.function.v(w_phrase) != 'Subj':
        return False
    
    # get all phrase atoms in the phrase    
    # exclude negations and conjunctions
    phrase_atoms = [phrs_at for phrs_at in L.d(w_phrase, otype='phrase_atom')
                        if F.typ.v(phrs_at) not in {'NegP','CP'}
                   ]
    
    # check whether the only phrase atom in the phrase is a prep. phrase
    if len(phrase_atoms) == 1 and F.typ.v(phrase_atoms[0]) == 'PP':
        
        # is a prepositional subject
        return True

    else:
        # is not a prep subj
        return False
    
    
def validate_subject(word):
    '''
    Return boolean on whether a word is a subject or not,
    i.e. a word without any modifiers that functions as subj.
    Require word node.
    
    Based on a supplied wordnode get phrase, phrase atom, and subphrase,
    features and compare them against a group of sets.
    Define those sets first. Then make the comparison.
    
    *Caution* 
    This function works reasonably well,
    but there are a number of edge cases that it does not catch.
    Fine-tuning this function would make a nice notebook in itself.
    See Gen 20:5 for a good edge case example, in which both היא pronouns
    are registered as subjects, but only one should be.
    '''
    
    # keep words with these part of speech tags
    keep_pdp = {'subs', # noun
                'nmpr', # proper noun
                'prps', # personal pronoun
                'prde', # demonstrative pronoun
                'prin'} # interrogative pronoun
                   
    # keep words in phrase_atoms with these type features
    keep_pa_typ = {'NP',   # noun phrase
                   'PrNP', # proper noun phrase
                   'PPrP', # personal pronoun phr.
                   'DPrP', # demonstrative pron. phr.
                   'IPrP'} # interrogative pron. phr.
    
    # exclude words in phrase_atoms with these relation features
    omit_pa_rela = {'Appo', # apposition
                    'Spec'} # specification
    
    # exclude words in subphrases with these relation features
    omit_sp_rela = {'rec', # nomens rectum
                    'adj', # adjectival 
                    'atr', # attributive
                    'mod', # modifier
                    'dem'} # demontrative
                        
    # get word's phrase, phrase atom, and subphrase, and subphrase relations
    w_phrase = L.u(word, otype='phrase')[0] # word's phrase node
    w_phrase_atom = L.u(word, otype='phrase_atom')[0] # word's phrase atom
    w_subphrases = L.u(word, otype='subphrase') # word's subphrase
    w_subphrs_relas = set(F.rela.v(sp) for sp in w_subphrases) # subphrs rela
    
    # compare word/phrase features against the sets
    if all([
            # word in subj phrase
            F.function.v(w_phrase) == 'Subj', 
            
            # phrase dependent part of speech is valid
            F.pdp.v(word) in keep_pdp,
            
            # either the word is in good phrase atom type 
            # or is part of a prepositional subj, e.g. with passives
            F.typ.v(w_phrase_atom) in keep_pa_typ\
                or is_preposition_subj(word),
            
            # phrase_atom relation is valid
            F.rela.v(w_phrase_atom) not in omit_pa_rela,
            
            # subphrase relation is valid
            not w_subphrs_relas & omit_sp_rela,
           ]):
        
        # word is a subject
        return True
    
    else:
        # word is not subject
        return False