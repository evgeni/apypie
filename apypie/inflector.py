# Based on ActiveSupport Inflector (https://github.com/rails/rails.git)
# Inflection rules taken from davidcelis's Inflections (https://github.com/davidcelis/inflections.git)

import re

try:
    from typing import List, Tuple
except ImportError:
    pass


class Inflections:

    def __init__(self):
        self.plurals = []
        self.singulars = []
        self.uncountables = []
        self.humans = []
        self.acronyms = {}
        self.acronym_regex = r'/(?=a)b/'

    def acronym(self, word):
        # type: (str) -> None
        self.acronyms[word.lower()] = word
        self.acronym_regex = '|'.join(self.acronyms.values())

    def plural(self, rule, replacement):
        # type: (str, str) -> None
        if rule in self.uncountables:
            self.uncountables.remove(rule)
        if replacement in self.uncountables:
            self.uncountables.remove(replacement)

        self.plurals.insert(0, (rule, replacement))

    def singular(self, rule, replacement):
        # type: (str, str) -> None
        if rule in self.uncountables:
            self.uncountables.remove(rule)
        if replacement in self.uncountables:
            self.uncountables.remove(replacement)

        self.singulars.insert(0, (rule, replacement))

    def irregular(self, singular, plural):
        # type: (str, str) -> None
        if singular in self.uncountables:
            self.uncountables.remove(singular)
        if plural in self.uncountables:
            self.uncountables.remove(plural)

        s0 = singular[0]
        srest = singular[1:]

        p0 = plural[0]
        prest = plural[1:]

        if s0.upper() == p0.upper():
            self.plural(r'(?i)({}){}$'.format(s0, srest), r'\1' + prest)
            self.plural(r'(?i)({}){}$'.format(p0, prest), r'\1' + prest)

            self.singular(r'(?i)({}){}$'.format(s0, srest), r'\1' + srest)
            self.singular(r'(?i)({}){}$'.format(p0, prest), r'\1' + srest)
        else:
            self.plural(r'{}(?i){}$'.format(s0.upper(), srest), p0.upper() + prest)
            self.plural(r'{}(?i){}$'.format(s0.lower(), srest), p0.lower() + prest)
            self.plural(r'{}(?i){}$'.format(p0.upper(), prest), p0.upper() + prest)
            self.plural(r'{}(?i){}$'.format(p0.lower(), prest), p0.lower() + prest)

            self.singular(r'{}(?i){}$'.format(s0.upper(), srest), s0.upper() + srest)
            self.singular(r'{}(?i){}$'.format(s0.lower(), srest), s0.lower() + srest)
            self.singular(r'{}(?i){}$'.format(p0.upper(), prest), s0.upper() + srest)
            self.singular(r'{}(?i){}$'.format(p0.lower(), prest), s0.lower() + srest)

    def uncountable(self, *words):
        self.uncountables.extend(words)

    def human(self, rule, replacement):
        # type: (str, str) -> None
        self.humans.insert(0, (rule, replacement))


class Inflector:

    def __init__(self):
        # type: () -> None
        self.inflections = Inflections()
        self.inflections.plural(r'$', 's')
        self.inflections.plural(r'(?i)([sxz]|[cs]h)$', r'\1es')
        self.inflections.plural(r'(?i)([^aeiouy]o)$', r'\1es')
        self.inflections.plural(r'(?i)([^aeiouy])y$', r'\1ies')

        self.inflections.singular(r'(?i)s$', r'')
        self.inflections.singular(r'(?i)(ss)$', r'\1')
        self.inflections.singular(r'([sxz]|[cs]h)es$', r'\1')
        self.inflections.singular(r'([^aeiouy]o)es$', r'\1')
        self.inflections.singular(r'(?i)([^aeiouy])ies$', r'\1y')

        self.inflections.irregular('child', 'children')
        self.inflections.irregular('man', 'men')
        self.inflections.irregular('medium', 'media')
        self.inflections.irregular('move', 'moves')
        self.inflections.irregular('person', 'people')
        self.inflections.irregular('self', 'selves')
        self.inflections.irregular('sex', 'sexes')

        self.inflections.uncountable('equipment', 'information', 'money', 'species', 'series', 'fish', 'sheep', 'police')

    def pluralize(self, word):
        # type: (str) -> str
        return self._apply_inflections(word, self.inflections.plurals)

    def singularize(self, word):
        # type: (str) -> str
        return self._apply_inflections(word, self.inflections.singulars)

    def _apply_inflections(self, word, rules):
        # type: (str, List[Tuple[str, str]]) -> str
        result = word

        if word != '' and result.lower() not in self.inflections.uncountables:
            for (rule, replacement) in rules:
                result = re.sub(rule, replacement, result)
                if result != word:
                    break

        return result
