
from .tokens import *
from .helper import cprint


def dump(tokens):
    
    s = ''
    for tp, token in tokens:

        if tp in [PLAINTEXT, OPERATION, COMMAND]:
            s += token

        if tp == FULLCOMMAND:
            s += token["name"] + '{' + '}{'.join(token["args"]) + '}'

    return s



def getClosingChar(txt, close='}', open_='{'):
    """
    find en lukket parantes

    >>> getClosingChar("{52+{21}}+10")
                 så findes -----^

    """

    depth = 0
    for i, c in enumerate(txt):

        depth += c == open_ and txt[i-1] != "\\"
        depth -= c == close and txt[i-1] != "\\"

        if depth == 0:
            return i


PARAOPEN = [i[0] for i in PARENTHESIS]
PARACLOSE = [i[1] for i in PARENTHESIS]

def translate(tokens):
    
    # parenterser
    # only 0 depth
    newTokens = []
    tempTokens = []

    isOpen = False
    isOpenCloser = ''
    depth = 0
    for tp, token in tokens:
        
        if token in PARAOPEN:

            depth += 1

            if depth > 1 or isOpen:
                tempTokens.append((tp, token))
                continue

            isOpen = True
            isOpenCloser = PARACLOSE[PARAOPEN.index(token)]
            tempTokens = []
        
        elif token in PARACLOSE:
            depth -= 1

            if depth > 0 or not isOpen or isOpenCloser != token:
                tempTokens.append((tp, token))
                continue

            newTokens.append((
                FULLCOMMAND, 
                {"name": PARENTHESIS[PARACLOSE.index(token)][2], "args":[dump(tempTokens)]
            }))
            isOpen = False

        elif isOpen:
            tempTokens.append((tp, token))

        else:
            newTokens.append((tp, token))

    return newTokens


def tokenize(raw):
    #0,4x^{3}+2*x^{2}+5*x+c_{0}
    #[('word', '0,4x'), ('command', '^'), ('arg', '{3}'), ('word','+2*x'), ('command', '^'), ('arg', '{2}'), ('word', '+5*x+c'), ('command', '_'), ('arg', '{0}')]

    # fjern shortcuts og kør altid med funktions ideen

    """
    
    [('word', '0,4x'), ('command', '^'), ('arg', '{3}'), ('word','+2*x'), ('command', '^'), ('arg', '{2}'), ('word', '+5*x+c'), ('command', '_'), ('arg', '{0}')]
    [('command', '^') ('arg', '0,4x'), ('arg', '{3}'), ('command', '^'), ('word','+2*x'), ('arg', '{2}'), ('word', '+5*x+c'), ('command', '_'), ('arg', '{0}')]
    
    """

    tokens = []

    offset = 0
    for i in range(len(raw)):
        isToken = False
        i += offset
        if i+1 > len(raw): break
        c = raw[i]

        if c == '{' and raw[i-1] != '\\':

            close = getClosingChar(raw[i:])
            tokens.append((ARGUMENT,raw[i+1:close+i]))
            offset += close
            continue

        # tokens
        for token in TOKENS:
                
            if raw[i:i+len(token)] != token:
                continue
            
            tokens.append((TOKENS[token],token))

            offset += len(token)-1

            isToken = True

        # arguments (parser kun højeste niveau)

        if isToken: continue

        # else
        tokens.append((PLAINTEXT,raw[i]))

    
    # tjek for ord
    # newtokens = []
    # word = ''
    # for clss, tok in tokens:

    #     # if clss == PLAINTEXT and tok in WORDFORCESEPERATORS:
    #     #     if word: newtokens.append((PLAINTEXT,word))
    #     #     newtokens.append((PLAINTEXT,tok))
    #     #     word = ''
    #     #     continue

    #     if clss == PLAINTEXT:
    #         word += tok
    #         continue

    #     elif word:
    #         newtokens.append((PLAINTEXT,word))
    #         word = ''
    #     newtokens.append((clss,tok))

    # if word:
    #     newtokens.append((PLAINTEXT,word))

    # return newtokens
    return tokens


def combine(tokens):
    """
    combine command with arguments
    """
    newtokens = []
    offset = 0
    for i in range(len(tokens)):
        i += offset

        if i+1 > len(tokens): break

        clss, tok = tokens[i]

        if type(clss) is tuple and clss[0] == COMMAND:
            args = []

            # get all leading args
            newoffset = -1
            for i, (subclss, subtok) in enumerate(tokens[i+1:]):

                if i >= clss[1]:
                    newoffset = i
                    break

                if subclss == ARGUMENT:
                    args.append(subtok)
                else:
                    break

            if newoffset == -1: newoffset = len(args)

            newtokens.append((FULLCOMMAND, {"name": tok, "args": args}))
            offset += newoffset
            continue

        newtokens.append((clss,tok))

    return newtokens


def catchDoubleBiCommands(tokens): #kan godt laves to multiple
    """
    altså helt ærligt kan jeg kun komme på et dumt eksempel

    x_{5}^{2} skal IKKE være 2*\super{\sub{x}{5}}{2}
    men istedet være en ny kommando \supersub{x}{5}{2}

    Burde også kun kunne ske ved bidirektionel kommandoer
    """

    newtokens = []
    ignoreCount = 0
    for i, tok in enumerate(tokens):

        if tok[0] == BIDIRECTIONALCMD:

            if ignoreCount > 0:
                ignoreCount -= 1
                continue

            # gå frem i sætningen og se om der kommer en makker
            for subtokNum, subtok in enumerate(tokens[i:]):
                if subtok[0] == BIDIRECTIONALCMD:
                    
                    combinedCommandName = DOUBLECOMMANDS.get((tok[1],subtok[1]), None)
                    if combinedCommandName:
                        ignoreCount = 1
                        newtokens.append((BIDIRECTIONALCMD,combinedCommandName))
                        break

                elif subtok[0] != ARGUMENT:
                    break

            if not combinedCommandName:
                newtokens.append(tok)

            continue
        
        newtokens.append(tok)

    return newtokens


def forceArgumentToStr(token):
    """
    forces token to be argument
    """

    if token[0] == FULLCOMMAND:
        return (ARGUMENT, '{'+token[1]["name"] +'{'+'}{'.join(token[1]["args"])+'}'+'}')

    if token[0] == ARGUMENT:
        return token

    else:
        return (ARGUMENT, '{'+token[1]+'}')


def rearrangeBidirection(tokens):
    """
    flyt rundt på fx x^2 til \sub{x}{2}
    """

    newtokens = []
    offset = 0
    for i in range(len(tokens)):
        i += offset
        if i+1 > len(tokens):break
        tok = tokens[i]

        if tok[0] == BIDIRECTIONALCMD:
            newtokens.pop(-1)

            newtokens.append((TOKENS[SHORTCUTTOKENS[tok[1]]], SHORTCUTTOKENS[tok[1]]))
            newtokens.append(forceArgumentToStr(tokens[i-1]))
            newtokens.append(forceArgumentToStr(tokens[i+1]))
            offset += 1
            continue
        
        newtokens.append(tok)

    return newtokens


def combineCharsToWords(tokens):
    if len(tokens) == 0: return tokens

    newtokens = [tokens[0]]
    aloneList = [" ", ","]

    for tp, tok in tokens[1:]:

        if tp != PLAINTEXT or newtokens[-1][0] != PLAINTEXT or tok in aloneList:
            newtokens.append((tp, tok))
            continue
        
        if newtokens[-1][1] in aloneList:
            newtokens.append((tp, tok))
            continue
        
        newtokens[-1] = (PLAINTEXT, newtokens[-1][1] + tok)

    return newtokens


def parse_(expr):
    print('---------S---------')
    expr = translate(expr)
    print(expr)
    tokens = tokenize(expr)
    cprint(tokens)
    tokens = combine(tokens)
    cprint(tokens)
    tokens = catchDoubleBiCommands(tokens)
    cprint(tokens)
    tokens = rearrangeBidirection(tokens)
    cprint(tokens)
    tokens = combine(tokens)
    cprint(tokens)

    print(expr, tokens)
    print('---------E----------')

    return tokens


def parse(expr):
    tokens = tokenize(expr)
    tokens = combine(tokens)
    tokens = translate(tokens)
    tokens = catchDoubleBiCommands(tokens)
    tokens = rearrangeBidirection(tokens)
    tokens = combine(tokens)
    tokens = combineCharsToWords(tokens)

    return tokens