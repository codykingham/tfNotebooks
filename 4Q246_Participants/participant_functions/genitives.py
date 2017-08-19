from __main__ import * # this module assumes the Text-Fabric methods have been globalized

def get_nomen_recta(regens):
    '''
    Return a list of the nomen rectums of a given nomen regens.
    The list contains nomen rectum subphrases 
    with the regens as their head.
    Require a word node that is the mother of a nom. rectum subphrase.
    '''
    
    # put nom. rectums here
    nom_rectums = []
        
    # get the nomen rectum (including the individual parts)
    # there will only be 1 match for a given nom. regem
    rectum = [rec for rec in E.mother.t(regens) 
                  if F.rela.v(rec) == 'rec'][0]

    # get the first word in the nomen rectum subphrase
    first_rectum_word = L.d(rectum, otype='word')[0]

    # get the first rectum's subphrase, but the one that is not 'rec'
    # this is to isolate the parallel subphrases
    rectum_in_series = [sp for sp in L.u(first_rectum_word, otype='subphrase')
                            if F.rela.v(sp) == 'NA']


    # the nomen regens is the only element
    # add it to the list
    if not rectum_in_series:
        nom_rectums.append(rectum)

    # the nomen regens may be the first element in a series
    # gather the other elements in the series and save them
    else:
        # collect rectums here
        all_rectums = []

        # for each rectum subphrase, look for a daughter subphrase that
        # is in a parallel relation that itself 
        # is contained within the nomens 'rectum'
        for rectum in rectum_in_series:

            # get the children of the first rectum that are 'parallel'
            # filter out any results that are not within the 'rectum' subphrase
            add_rectums = [sp for sp in E.mother.t(rectum)

                               # subphrase must be in a parallel relation
                               if F.rela.v(sp) == 'par'

                               # first word in subphrase must be contained
                               # within the rectum subphrase
                               and 'rec' in set(F.rela.v(sp) for sp in 
                                                 L.u(
                                                     L.d(sp, otype='word')[0], # 1st wrd
                                                     otype='subphrase'
                                                    ) 
                                                )
                          ]

            # add the additional rectums to the complete list
            all_rectums.extend(add_rectums)

        # add in the first rectum
        all_rectums.insert(0, rectum_in_series[0])

        # add the rectums
        nom_rectums.extend(all_rectums) 

    return nom_rectums
