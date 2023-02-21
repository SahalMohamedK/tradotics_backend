def human_delta(tdelta):
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['min'] is 0:
        fmt = '{sec} sec'
    elif d['hrs'] is 0:
        fmt = '{min} min {sec} sec'
    elif d['days'] is 0:
        fmt = '{hrs} hr(s) {min} min {sec} sec'
    else:
        fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'

    return fmt.format(**d)

def safeDevide(a, b, otherwise = 0):
    return (a/b) if b > 0 else otherwise