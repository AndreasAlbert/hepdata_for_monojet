
def treat_overflow(arr):
    """
    Merges the overflow bin into the last bin
    """
    ret =  arr[:-1]
    ret[-1] = ret[-1] + arr[-1]
    return ret