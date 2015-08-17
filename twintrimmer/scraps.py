def is_substring(string1, string2):
    '''
    Returns a match if one string is a substring of the other

    :param str string1: the first string to compare
    :param str string2: the second string to compare
    :returns: True if either string is substring of the other
    :rtype: bool

    For example:

    >>> is_substring('this', 'this1')
    True
    >>> is_substring('that1', 'that')
    True
    >>> is_substring('that', 'this')
    False
    '''
    return string1 in string2 or string2 in string1
