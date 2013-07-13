
def parse_file(fileloc, default_category="Expletives"):
    categories = {}
    with open(fileloc, 'rU') as filterFile:
        category = default_category
        categories[category] = []
        for line in filterFile:
            line = line.strip()
            if len(line) and not line.startswith('#'):
                # Check if line defines a new category
                if line.startswith('Category:'):
                    category = line.split(':', 1)[-1].strip()
                    if category not in categories:
                        categories[category] = []
                    continue

                # Check if line contains a severity rank
                if ':' in line:
                    expr, severity = line.split(':', 1)
                else:
                    # Make default severity rank 10 (most severe)
                    expr = line
                    severity = '10'

                #asRegex = expr.strip().lower().replace('*', '\w*')
                word = expr.strip().lower()
                asInt = int(severity.strip())
                categories[category].append((word, asInt))

    return categories


def get_blocked_tuples(categories, severities):
    words = []
    for key, value in severities.iteritems():
        if not value:
            print "Not blocking words of category: " + key
            continue
        if key in categories:
            words.extend(get_tuples_ge_severity(categories[key], value))
        else:
            print "WARNING: the category " + key + " is not in the filter file, ignoring it"
    return words


def is_blocked(severity, category_name, severities):
    if category_name in severities and severities[category_name]:
        return severity >= severities[category_name]
    return False

def get_all_words(categories):
    list = []
    for tuples in categories.values():
        list.extend(get_word_list(tuples))
    return list


def get_word_list(tuples):
    return [word for word, severity in tuples]


def get_tuples_ge_severity(tuples, low):
    return [(word, severity) for word, severity in tuples if severity >= low]


if __name__ == "__main__":
    import sys
    severities = {'Expletives': 6}
    filename = sys.argv[1]
    categories = parse_file(filename)
    blocked_words = get_blocked_tuples(categories, severities)
    print blocked_words

