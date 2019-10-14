import re
import unicodedata

_nonbmp = re.compile(r'[\U00010000-\U0010FFFF]')


def _surrogatepair(match):
    char = match.group()
    assert ord(char) > 0xffff
    encoded = char.encode('utf-16-le')
    return (
        chr(int.from_bytes(encoded[:2], 'little')) +
        chr(int.from_bytes(encoded[2:], 'little')))


def with_surrogates(text):
    return _nonbmp.sub(_surrogatepair, text)


def add_emotes(stri):
    out = stri
    for find in re.findall(":([^:]*)", stri):
        try:
            out = out.replace(':{}:'.format(find), unicodedata.lookup(find))
        except KeyError:
            pass
    return out
