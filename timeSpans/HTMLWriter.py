import itertools

def writeHTML(clauseDict, spanDict, title):
    '''
    compile HTML code to display:
        1. plain text clauses
        2. indent clauses based on relationship to each other
        3. shade each clause within each time-span
    '''
    
    # open and assign the required HTML templates: 
    with open('HTMLTemplates/doc.txt') as docTemplate,\
         open('HTMLTemplates/dataPlain.txt') as dataPlainTemplate,\
         open('HTMLTemplates/dataColor.txt') as dataColorTemplate:
        document = docTemplate.read()
        dataPlain = dataPlainTemplate.read().replace('\n','').replace('\t','')
        dataColor = dataColorTemplate.read().replace('\n','').replace('\t','')

    # basic HTML characters/formatting 
    formatting = {
                'tab' : '&nbsp&nbsp&nbsp&nbsp',
                'colors' : itertools.cycle(('#addfff','#a3e2a1'))
                 }

    # clauses in this set will receive color formatting
    inTimeSpan = set(clause for span in spanDict 
                     for clause in spanDict[span])
    
    HTMLBody = ''

    for clause, clauseData in clauseDict.items():

        if clause in spanDict:    # receives special formatting
            firstClause = clause
            switchColor = next(formatting['colors'])
            for spanClause in spanDict[firstClause]:
                spanClauseData = clauseDict[spanClause]
                currentColor = switchColor
                clauseLabel = formatting['tab'] + spanClause
                indentation = formatting['tab'] * spanClauseData['indentation']
                text = spanClauseData['text'] + indentation
                formattedClause = dataColor.format(color=currentColor, # fill HTML template
                                                   text=text,
                                                   label=clauseLabel)
                HTMLBody += formattedClause # full code
                
        elif clause not in inTimeSpan: # do not receive special formatting
            clauseLabel = formatting['tab'] + clause
            indentation = formatting['tab'] * clauseData['indentation']
            text = clauseData['text'] + indentation
            formattedClause = dataPlain.format(text=text,
                                               label=clauseLabel)
            HTMLBody += formattedClause
            
        else:
            continue
            
    HTMLDocument = document.format(data=HTMLBody,
                                   title=title)
    return HTMLDocument