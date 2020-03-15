
import base64
import re
import json

LIST_FILE = r"gfwlist.txt"



TYPE_WILDCARD = 1
TYPE_REG_EXP  = 2

PROTOCOLS_ALL   = 1
PROTOCOLS_HTTP  = 2
PROTOCOLS_HTTPS = 4


def parse(line):
    foxy_pattern = {"title": "",
                    "pattern": "",
                    "type": TYPE_REG_EXP,
                    "protocols": PROTOCOLS_ALL,
                    "active": True
                    }
    # regex already
    if line[0] == '/' and line[-1] == ""/"":
        # remove https?:\/\/[^\/]+
        rline = line[1:-1]
        pattern = rline.replace(r"^https?:\/\/", r"^")
        # delete paths
        match = re.match(r".{5,}?\\\/", pattern)
        if match:
            pattern = match.group(0)[:-2]
        foxy_pattern["pattern"] = pattern
        # foxy_pattern["protocols"] = PROTOCOLS_ALL
        foxy_pattern["title"] = re.search(r"\.?[\w][\w\.]+", pattern).group(0)
    elif line.startswith("||"):
        rline = line[2:]
        foxy_pattern["title"] = rline
        foxy_pattern["pattern"] = re.escape(rline).replace(r"\*", ".*")
    elif line.startswith("|"):
        rline = line[1:]
        if rline.startswith("http://"):
            rline = rline.replace(r"http://", "")
            foxy_pattern["protocols"] = PROTOCOLS_HTTP
        elif rline.startswith("https://"):
            rline = rline.replace(r"https://", "")
            foxy_pattern["protocols"] = PROTOCOLS_HTTPS
        rline = rline.split('/')[0]
        foxy_pattern["title"] = rline
        foxy_pattern["pattern"] = "^" + re.escape(rline).replace(r"\*", ".*")
    else:
        rline = line
        if rline.startswith("http://"):
            rline = rline.replace(r'http://', '')
            foxy_pattern["protocols"] = PROTOCOLS_HTTP
        elif rline.startswith("https://"):
            rline = rline.replace(r"https://", "")
            foxy_pattern["protocols"] = PROTOCOLS_HTTPS
        rline = rline.split("/")[0]
        foxy_pattern["title"] = rline
        foxy_pattern["pattern"] = re.escape(rline).replace(r"\*", ".*")
    return foxy_pattern


def join(gfwlist):
    patterns = \
        {
            "whitePatterns": [],
            "blackPatterns": []
        }
    for l in gfwlist.split('\n'):
        # l = l[:-1]
        if not l or l[0] == '!' or l[0] == '[':
            continue
        if l.startswith('@@'):
            patterns["blackPatterns"].append(parse(l[2:]))
        else:
            patterns["whitePatterns"].append(parse(l))
    return patterns


def main():
    with open(LIST_FILE, 'r') as file:
        gfwlist = file.read()
    rules = base64.b64decode(gfwlist).decode()
    patterns = join(rules)
    with open("gfwlist_patterns.json", "w") as file:
        file.write(json.dumps(patterns, indent=2))


if __name__ == '__main__':
    main()