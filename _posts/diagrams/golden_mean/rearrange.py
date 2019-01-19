#!/usr/bin/env python

from __future__ import print_function
import sys
import argparse
import networkx as nx
from networkx.algorithms import community
import matplotlib.pyplot as plt
import csv

def printGraph(G, name='Graph'):
    print('\n{}, {} nodes:'.format(name, G.order()))
    for n in sortedByWeight(G):
        print(n, G.nodes()[n]['weight'], list(G.neighbors(n)))

def computeWeights(G):
    ''' Computes the weights for the given graph '''
    linkFactor = 0.25
    for n in G.nodes():
        weight = float(len(list(G.neighbors(n))))
        for nn in G.neighbors(n):
            weight += linkFactor * float(len(list(G.neighbors(nn))))
        G.nodes[n]['weight'] = weight

def computeWeightsForNodes(G, nodes):
    ''' Computes the weights for the given graph '''
    linkFactor = 0.25
    for n in nodes:
        nlist = [x for x in G.neighbors(n) if x in nodes]
        weight = float(len(nlist))
        for nn in nlist:
            nlist2 = [x for x in G.neighbors(nn) if x in nodes]
            weight += linkFactor * float(len(nlist2))
        G.nodes[n]['weight'] = weight

def sortedByWeight(G, nodes = None):
    if not nodes:
        nodes = G.nodes()
    return sorted(nodes, key=lambda n: -G.nodes()[n]['weight'])

def nextAdjecent(G, nodes):
    for n in nodes:
        for nn in G.neighbors(n):
            yield nn
    yield None

def printParts(parts):
    print('Parts:')
    for part in parts:
        print(part)

def getPartsOfNodes(parts):
    res = {}
    for i in range(len(parts)):
        for n in parts[i]:
            res[n] = i
    return res

def partition(G, k=3, addFirstSiblings=True):
    if G.order() <= k:
        return [G.nodes()]

    # Compute the weights of the nodes
    computeWeights(G)
    remaining = sortedByWeight(G)

    parts = [None] * k

    # Step 1: Initial distribution.
    # The item with the highest weight goes to the first part, with all its links;
    # do the same for the first k items
    for i in range(k):
        # After the first extraction, re-evaluate the weights and resort
        if i>0:
            computeWeightsForNodes(G, remaining)
            remaining = sortedByWeight(G, remaining)

        # Add the node with the highest weight to the appropriate part
        winner = remaining[0]
        parts[i] = [winner]
        remaining.remove(winner)

        # Also add all its remaining siblings
        if addFirstSiblings:
            for sibling in G.neighbors(winner):
                if sibling in remaining:
                    parts[i].append(sibling)
                    remaining.remove(sibling)

    # Step 2: distribute remaining elements to the graph; use a round-robin algorithm
    gens = [nextAdjecent(G, parts[i]) for i in range(k)]
    i = 0
    while remaining:
        valueFound = None
        if not gens[i]:
            gens[i] = nextAdjecent(G, parts[i])
        while True:
            val = next(gens[i])
            if not val:
                break
            if val and val in remaining:
                valueFound = val
                break
        # If we can't get anymore elements, try resetting the generator
        if not valueFound:
            gens[i] = nextAdjecent(G, parts[i])
            # Try again
            while True:
                val = next(gens[i])
                if not val:
                    gens[i] = None
                    break
                if val and val in remaining:
                    valueFound = val
                    break

        # TODO: what happens if we don't find a value

        # Distribute the found value to the right bucket
        if valueFound:
            parts[i].append(valueFound)
            remaining.remove(valueFound)

        i = (i+1) % k

    # print('Parts orig:')
    # for part in parts:
    #     print(sorted(part))
    # print('')


    # Step 3: k-means rebalancing
    partsOfNodes = getPartsOfNodes(parts)
    minPartSize = G.order()/k/2;
    print(minPartSize, file=sys.stderr)
    # scores = {}
    # maxScorePerNode = {}
    # for n in G.nodes():
    #     scores[n] = [0.0] * k
    for _ in range(100):
        lens = [len(x) for x in parts]

        # Compute the movement scores for each node
        # Movement score = (score, curPartIdx, destPartIdx) pair
        movementScores = {}

        for n in G.nodes():
            # Compute the score of the node, as if is was in any of the parts
            # Score for a part = num of neighbors in that part
            # At the end subtract from all the scores the score corresponding to the current part
            # to make sure that the score for the current part is always 0;
            # movement is indicated by a score > 0
            curPartIdx = partsOfNodes[n]
            countPerPart = [0] * k
            for nn in G.neighbors(n):
                countPerPart[partsOfNodes[nn]] += 1
            curPartCount = countPerPart[curPartIdx]
            for j in range(k):
                countPerPart[j] -= curPartCount
            score = max(countPerPart)
            destPartIdx = countPerPart.index(score)
            movementScores[n] = (score, curPartIdx, destPartIdx)

        # Get the node with the max score
        # Ensure that we don't take too much from one part
        selected = None
        maxScore = 0
        curPartIdxOfSelected = 0
        destPartIdxOfSelected = 0
        for n, (score, curPartIdx, destPartIdx) in movementScores.items():
            # if n == 18:
            #     print(n, score, curPartIdx, destPartIdx)
            if score > maxScore and len(parts[curPartIdx]) > minPartSize:
                selected = n
                maxScore = score
                curPartIdxOfSelected = curPartIdx
                destPartIdxOfSelected = destPartIdx

        # If we couldn't find any node with a positive score, we can't make any move
        if not selected:
            break

        # TODO: keep a list of discounts for each node; if one node is moved, it will be discounted
        # the next time we want to move a node, we try the non-discounted nodes

        # Move the selected node
        # print('{}: {} -> {} -- score={}'.format(selected, curPartIdxOfSelected, destPartIdxOfSelected, maxScore))
        parts[curPartIdxOfSelected].remove(selected)
        parts[destPartIdxOfSelected].append(selected)
        partsOfNodes[selected] = destPartIdxOfSelected

    # print('Parts:')
    # for part in parts:
    #     print(part)

    return parts

def printPlantUml(parts, linksPairs):
    print('@startuml\n')
    # Dump the nodes definitions
    for i in range(len(parts)):
        print('package P{} {}'.format(i+1, '{'))
        for n in parts[i]:
            print('    agent N{}'.format(n))
        print('}')

    # Dump the links
    partsOfNodes = getPartsOfNodes(parts)
    partsLinks = []
    inPartLinks = []
    for pair in linksPairs:
        first = pair[0]
        second = pair[1]
        idx1 = partsOfNodes[first]
        idx2 = partsOfNodes[second]
        if idx1 == idx2:
            inPartLinks.append(pair)
        else:
            if idx1 > idx2:
                idx1, idx2 = idx2, idx1
            ppair = (idx1+1, idx2+1)
            if ppair not in partsLinks:
                partsLinks.append(ppair)
    print('')
    for p in partsLinks:
        first = p[0]
        second = p[1]
        print('P{} -- P{}'.format(first, second))
    print('')
    for p in inPartLinks:
        first = p[0]
        second = p[1]
        print('N{} -- N{}'.format(first, second))
    # print('')
    # for p in inPartLinks:
    #     first = p[0]
    #     second = p[1]
    #     if first in parts[0]:
    #         print('N{} -- N{}'.format(first, second))


    print('\n@enduml')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inFile', action='store', nargs='?',
        help='The CSV file with links')
    parser.add_argument('numParts', action='store', nargs='?', type=int,
        help='The number of parts to use')
    parser.add_argument('--dontAddFirstSiblings', action='store_true',
        help='The number of parts to use')
    args = parser.parse_args()

    linksPairs = []
    with open(args.inFile, 'r') as csvfile:
        csvReader = csv.reader(csvfile)
        for line in csvReader:
            first = int(line[0])
            second = int(line[1])
            pair = (first, second)
            linksPairs.append(pair)


    # Create the graph
    G = nx.Graph()
    G.add_edges_from(linksPairs)

    parts = partition(G, args.numParts, not args.dontAddFirstSiblings)

    # Print PlantUml format
    printPlantUml(parts, linksPairs)


    # Print the nodes
    # printGraph(G)

    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, with_labels=True)
    # colors = ['r', 'b', 'g', 'm', 'y', 'orange', 'olive', 'gold']
    # for i in range(len(parts)):
    #     nx.draw_networkx_nodes(G, pos,
    #                        nodelist=parts[i],
    #                        node_color=colors[i])
    # plt.show()

if __name__ == "__main__":
    main()

