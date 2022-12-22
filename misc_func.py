

import datetime
import json


import numpy as np

import string

def fmtcols(indent:int, mylist: list, cols: int):
    """makes neetly printed lists in columns,
    stolen from S.Lott https://stackoverflow.com/questions/171662/formatting-a-list-of-text-into-columns#173823

    Args:
        mylist (list): _description_
        cols (int): _description_

    Returns:
        _type_: _description_
    """

    lines = (indent*"    "+"\t".join((str(x) for x in mylist[i:i+cols])) for i in range(0,len(mylist),cols))
    return '\n'.join(lines)


def fmt_score_log(*args,**kwargs):
    indent = kwargs.get('indent',2)
    cols = kwargs.get('cols',2)
    col_sep = kwargs.get('col_sep',3)
    
    indat = [ str(x) for x in list(zip(range(len(args[0])),*args)) ]
    
    col_len = max( len(x) for x in indat ) + col_sep
    indat = [ x.ljust(col_len) for x in indat ]
    # print(col_len)
    
    lines = (indent*"    "+"".join( indat[i:i+cols] ) for i in range(0,len(indat),cols))
    return '\n'.join(lines)
