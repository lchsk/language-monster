import re

def parse_line(line):
    """Parse data from a line."""

    line = line.split('||')

    columns = 6

    assert len(line) == columns, 'Invalid format: should be {0} columns'.format(columns)

    # base, target, english, comments, pos

    base_en, target_en = '', ''
    b, t, pop, en, c, pos = line
    from_english = '{{from_english}}' in c
    english_invalid = '{{english_invalid}}' in c
    verified = '{{verified}}' in c

    r = re.findall(r'\{([^{}]+)\}', c)

    for pair in r:
        tmp = pair.split('=')

        if len(tmp) != 2:
            continue

        if tmp[0] == 'base':
            base_en = tmp[1]
        elif tmp[0] == 'target':
            target_en = tmp[1]

    pair = dict(
        b=b.strip(),
        t=t.strip(),
        en=en,
        c=c,
        base_en=base_en,
        target_en=target_en,
        from_english=from_english,
        english_invalid=english_invalid,
        verified=verified,
        pop=pop,
        pos=pos,
    )

    for key, value in pair.iteritems():
        pair[key] = value.decode('utf-8') if type(value) == str else value

    return pair
