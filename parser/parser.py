
from .tokens import *
from .helper import cprint

def getClosingChar(txt, close='}', open_='{'):
    """
    find en lukket parantes

    >>> getClosingChar("{52+{21}}+10")
                 så findes -----^

    """

    depth = 0
    for i, c in enumerate(txt):

        depth += c == open_
        depth -= c == close

        if depth == 0:
            return i


def translate(expr):
    
    for o, c, macro in PARENTHESIS:
        expr = expr.replace(o, macro+'{')
        expr = expr.replace(c, '}')
    
    return expr


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

        if c == '{':
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

        if clss == COMMAND:
            args = []

            # get all leading args
            for subclss, subtok in tokens[i+1:]:

                if subclss == ARGUMENT:
                    args.append(subtok)
                else:
                    break

            newtokens.append((FULLCOMMAND, {"name": tok, "args": args}))
            offset += len(args)
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

            newtokens.append((COMMAND,SHORTCUTTOKENS[tok[1]]))
            newtokens.append(forceArgumentToStr(tokens[i-1]))
            newtokens.append(forceArgumentToStr(tokens[i+1]))
            offset += 1
            continue
        
        newtokens.append(tok)

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
    expr = translate(expr)
    tokens = tokenize(expr)
    tokens = combine(tokens)
    tokens = catchDoubleBiCommands(tokens)
    tokens = rearrangeBidirection(tokens)
    tokens = combine(tokens)
    return tokens