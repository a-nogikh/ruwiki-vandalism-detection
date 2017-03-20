import sys
#  http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def bucket_items(raw, bucket_size):
    curr_list = []
    for item in raw:
        curr_list.append(item)
        if len(curr_list) >= bucket_size:
            yield curr_list
            curr_list = []

    if len(curr_list) > 0:
        yield curr_list


def strip_comment(text):
    if text is None:
        return ""

    exclude_to = text.rfind("*/")
    if exclude_to >= 0:
        return text[exclude_to + 2:].strip()
    else:
        return text.strip()