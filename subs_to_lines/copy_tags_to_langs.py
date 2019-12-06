#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import pprint

# eng = r"<ffx:amp_2> Don't think it was all in vain... You saved us all. <ffx:wonder>And Kirill... I'll give him this watch and make sure he gets out of this hellhole. <ffx:neutral>You have my word."
# ru = r"Не думай, что все было зря... Ты всех нас спас. А Кирилл... Я передам ему часы и прослежу, чтобы он выбрался из этой дыры. Обещаю."
tag_closing = '>'
# if dot split length is eqaul
# Takes tags from the start and from the end.
# Not from the middle of the phrase

# Replaces all triple and double signs


def normalize_marks(val):
    signs = ['!!!', '!!', '?!', '!?', '!!?',
             '!??', '???', '??', '?', '...', '..']

    for s in signs:
        val = val.replace(s, '.')

    val = val.replace(',', '')
    return val


def normalize_spaces(val):
    val = val.replace('>', '> ')
    val = val.replace('<', ' <')
    return ' '.join(val.split())


def delete_tags(val):
    filtered_val = [v for v in val.split(' ') if tag_closing not in v]
    return ' '.join(filtered_val)


def get_tags(val):
    search_deep = 2
    tags = []

    words = val.split()
    if len(words) < search_deep:
        search_deep = len(words)

    for id in range(search_deep):
        if tag_closing in words[id]:
            tags.append(words[id])

    return tags


def get_tags_data(val):
    val = normalize_marks(normalize_spaces(val))
    tag_data = {}
    sentences = val.split('.')

    for i, text in enumerate(sentences):
        tag_data[i] = get_tags(text)

    return tag_data


def add_tags_data(data, val):
    val = normalize_marks(normalize_spaces(val))
    val = delete_tags(val)
    sentences = val.split('.')
    tagged_val = []

    if len(data) == len(sentences):

        for i, tags in data.iteritems():
            tagged_val.append(' '.join(tags) + ' ' + sentences[i])
    else:
        for i, text in enumerate(sentences):
            if i == 0:
                tagged_val.append(' '.join(data[i]) + ' ' + text)
            else:
                tagged_val.append(text)

    tagged = '. '.join(tagged_val)
    return ' '.join(tagged.split())
