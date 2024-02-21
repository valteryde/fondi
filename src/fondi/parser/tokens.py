
BIDIRECTIONALCMD = 'bicmd'
COMMAND = 'macro'
FULLCOMMAND = 'fmacro'
PLAINTEXT = 'char'
ARGUMENT = 'arg'
OPERATION = 'opera'

TOKENSCOLOR = {
    BIDIRECTIONALCMD:'\033[91m',
    COMMAND: '\033[92m',
    ARGUMENT: '\033[94m',
    OPERATION: '\033[93m',
    FULLCOMMAND: '\033[1m\033[92m',
    PLAINTEXT: "",
}

TOKENS = {
    "\\frac": COMMAND,
    "\\super": COMMAND,
    "\\sub": COMMAND,
    "\\para": COMMAND,
    "\\squarepara": COMMAND,
    "\\cases": COMMAND,
    "\\text": COMMAND,
    "\\sqrt": COMMAND,
    "\\quad": COMMAND,
    "\\,": COMMAND,
    "\\:": COMMAND,
    "\\;": COMMAND,
    "\\!": COMMAND,
    "\\smallSpace": COMMAND,
    "\\qquad": COMMAND,
    "^_": BIDIRECTIONALCMD,
    "_^": BIDIRECTIONALCMD,
    "^": BIDIRECTIONALCMD,
    "_": BIDIRECTIONALCMD,
    # "+": OPERATION,
    # "-": OPERATION,
    # "*": OPERATION,
    # "·": OPERATION,
    "=": OPERATION,
    ">": OPERATION,
    "<": OPERATION,
}

SHORTCUTTOKENS = {
    "^": "\\super",
    "_": "\\sub",
    "^_": "\\supersub",
    "_^": "\\subsuper",
}

DOUBLECOMMANDS = {
    ('^', '_'): "^_",
    ('_', '^'): "_^"
}

PARENTHESIS = {
    ("(",')', '\\para'),
    ('[', ']', '\\squarepara'),
}

### MORE TOKENS
TOKENS["\\alpha"] = COMMAND
TOKENS["\\beta"] = COMMAND
TOKENS["\\gamma"] = COMMAND
TOKENS["\\Gamma"] = COMMAND
TOKENS["\\delta"] = COMMAND
TOKENS["\\Delta"] = COMMAND
TOKENS["\\eta"] = COMMAND
TOKENS["\\epsilon"] = COMMAND
TOKENS["\\theta"] = COMMAND
TOKENS["\\kappa"] = COMMAND
TOKENS["\\kappa"] = COMMAND
TOKENS["\\lambda"] = COMMAND
TOKENS["\\tau"] = COMMAND
TOKENS["\\sigma"] = COMMAND
TOKENS["\\Sigma"] = COMMAND
TOKENS["\\phi"] = COMMAND
TOKENS["\\chi"] = COMMAND
TOKENS["\\psi"] = COMMAND
TOKENS["\\omega"] = COMMAND
TOKENS["\\Omega"] = COMMAND
TOKENS["\\pi"] = COMMAND
