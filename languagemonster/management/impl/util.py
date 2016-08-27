import re

def parse_line(line):
    """Parse data from a line."""

    line = line.split('||')

    columns = 5

    assert len(line) == columns, 'Invalid format: should be {0} columns'.format(columns)

    # base, target, english, comments

    base_en, target_en = '', ''
    b, t, pop, en, c = line[0], line[1], line[2], line[3], line[4]
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
        pop=pop
    )

    return pair
