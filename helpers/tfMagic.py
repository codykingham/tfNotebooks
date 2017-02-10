class Magic():
    '''
    A class to supercharge TF nodes with flexible data requests.
    
    Magic can return a requested feature whether it is loaded or not.
    It can also return a container or contained object type with ease.
    Requires a string request which is either a feature or object type.

    *Important: Text-Fabric must be instantiated as 'TF' in order 
    for Magic to determine which object to call the additional load instructions on. 

    example use:
    phrase_nodes = [605144, 605145]
    magic_nodes = [Magic(node) for node in phrase_nodes]
    magic_nodes[0].get('clause_atom')
    OUT: 514582
    '''
    
    # all object types in descending, hierarchical order
    otypes = ('book', 'chapter', 'verse', 'half_verse', 
             'sentence', 'sentence_atom', 'clause', 
             'clause_atom', 'phrase', 'phrase_atom', 
             'subphrase', 'lex', 'word')
    
    # give each object a depth number for determining whether L.u or L.d needed
    otype_depth = dict(
                        (otype, i) for (i, otype) in enumerate(otypes)
                      )
    
    def __init__(self, node):
        self.node = node
        
    def get(self, request_string):
        '''
        Get a requested feature or container/contained object.
        Get will load a feature if it is not present already.
        It will determine whether a L.u or L.d is needed for objects.
        '''
        
        from __main__ import F, L, TF
        
        # get the TF objects
        #global F
       
        # return requested embedding/embedded object types
        if request_string in self.otypes:
            
            this_otype = F.otype.v(self.node) # otype string
            node_depth = self.otype_depth[this_otype] # depth of current otype
            request_depth = self.otype_depth[request_string] # depth of request
            
            # determine whether L.u or L.d needed
            if node_depth > request_depth: # L.u if lower
                return L.u(self.node, otype=request_string)[0] # index for simple return value
            
            else: # L.d 
                return L.d(self.node, otype=request_string)
            
        # return requested feature
        else:
            
             # try the feature call
            try:
                feature = eval('F.{feature}.v({node})'.format(feature=request_string,
                                                              node = self.node))
            # if feature not present, load it
            except AttributeError:
                # load the feature into TF
                TF.load(request_string, add=True)
                # format it
                feature = eval('F.{feature}.v({node})'.format(feature=request_string,
                                                              node = self.node))
                
            # return the value
            return feature