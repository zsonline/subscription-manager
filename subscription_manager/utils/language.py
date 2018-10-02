def humanize_list(list, conjunction):
    """
    Converts a given list into a string by
    combining all elements to an enumeration
    with conjunction between the last two elements.
    """
    if len(list) == 0:
        return ''
    if len(list) == 1:
        return str(list[0])
    if len(list) == 2:
        return str(list[0]) + ' ' + conjunction + ' ' + list[1]
    humanized = ''
    for elem in list[:-2]:
        humanized += str(elem) + ', '
    humanized += humanize_list(list[-2:], conjunction)
    return humanized