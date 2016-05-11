#!/usr/bin/env python

"""
build trie from (partial) export of WORMS database
"""

from collections import namedtuple
from pickle import dump

import csv
import logging

log = logging.getLogger(__name__)


# Tuple representing an entity with a rank, list of tokens, unique id
Entity = namedtuple('Entity', ('rank', 'tokens', 'id'))


def read_worms_entities(csv_fname):
    """
    Read export of tu_matrix table from WORMS database in CSV format
    """
    entities = []

    log.info('reading entities from file ' + csv_fname)

    with open(csv_fname, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            entity = Entity(row[1], row[2].split(), row[0])
            entities.append(entity)

    log.info('{} entites'.format(len(entities)))
    return entities


# Tuple representing a node in the trie with properties 'ids' and 'children'.
# 'ids' lists the id of each entity whose tokens equal the path through the trie,
# possibly an empty list for non-terminal nodes.
# 'children' is a dict mapping tokens to child nodes, representing further paths
# down the trie.
Node = namedtuple('Node', ('ids', 'ranks', 'children'))


def build_trie(entities):
    """
    Build a trie from entities for fast matching of token sequences to entities
    """
    trie = Node([], [], {})
    node_count = 1
    token_count = 0

    for rank, tokens, id in entities:
        node = trie
        token_count += len(tokens)

        for token in tokens:
            # traverse trie, adding new nodes where required
            try:
                node = node.children[token]
            except KeyError:
                new_node = Node([], [], {})
                node.children[token] = new_node
                node = new_node
                node_count += 1

        node.ids.append(id)
        node.ranks.append(rank)

    log.info('{} tokens'.format(token_count))
    log.info('{} trie nodes'.format(node_count))
    return trie


def dump_trie(trie, pkl_fname):
    log.info('writing trie to file ' + pkl_fname)
    dump(trie, open(pkl_fname, 'wb'))


# utility/debug functions


def print_node(node, indent=0):
    for child_token, child_node in node.children.items():
        print(indent * ' ' + child_token, child_node.ids or '')
        print_node(child_node, indent + 4)


def print_trie(node, start_token):
    print(start_token, node.ids)
    print_node(node.children[start_token], 4)


if __name__ == '__main__':
    # Usage example:
    # wormsner/build_trie.py ../tu_matrix.csv ../worms_trie.pkl
    import sys
    logging.basicConfig(level=logging.DEBUG)
    csv_fname, pkl_fname = sys.argv[1:3]
    entities = read_worms_entities(csv_fname)
    trie = build_trie(entities)
    #print_trie(trie, 'Medigidiella')
    dump_trie(trie, pkl_fname)
