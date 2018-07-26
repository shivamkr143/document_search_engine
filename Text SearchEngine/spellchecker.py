import re
from collections import defaultdict
import os.path

WORDFILE = '/home/sashib/Downloads/RankingSubmission/w.dat'
class SpellChecker(object):

    def words(text):
        return re.findall('[a-z]+', text.lower())

    def train(features):
        model = defaultdict(int)
        for f in features:
            model[f] += 1
        return model

    NWORDS = train(words(
        " ".join(
            set([w.lower() for w in open(WORDFILE).read().splitlines()])
        )
    ))

    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def _edits1(self, word):
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
        replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts = [a + c + b for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)

    def _known_edits2(self, word):
        return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self.NWORDS)

    def _known(self, words):
        return set(w for w in words if w in self.NWORDS)

    def correct_token(self, token):
        candidates = self._known([token]) or self._known(self._edits1(token)) or self._known_edits2(token) or [token]
        return max(candidates, key=self.NWORDS.get)

    def correct_phrase(self, text):
        tokens = text.split()
        return [self.correct_token(token) for token in tokens]


if __name__ == '__main__':
    spellchecker = SpellChecker()
    while True:
        word = raw_input("Enter a word: ").lower()
        tokens = spellchecker.correct_phrase(word)
        out = " ".join(str(s) for s in tokens)
        print out