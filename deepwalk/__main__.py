#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
import logging

from deepwalk import graph, walks

# --

import psutil
from multiprocessing import cpu_count

p = psutil.Process(os.getpid())
try:
    p.set_cpu_affinity(list(range(cpu_count())))
except AttributeError:
    try:
        p.cpu_affinity(list(range(cpu_count())))
    except AttributeError:
        pass

logger = logging.getLogger(__name__)
LOGFORMAT = "%(asctime).19s %(levelname)s %(filename)s: %(lineno)s %(message)s"

# --

def load_graph(args):
  print >> sys.stderr, "Loading graph..."
  
  if args.format == "adjlist":
    G = graph.load_adjacencylist(args.input, undirected=args.undirected)
  elif args.format == "edgelist":
    G = graph.load_edgelist(args.input, undirected=args.undirected)
  else:
    raise Exception("Unknown file format: '%s'.  Valid formats: 'adjlist', 'edgelist'" % args.format)
  
  return G  


def process(args):
  G = load_graph(args)
  num_walks = len(G.nodes()) * args.number_walks
  data_size = num_walks * args.walk_length
  
  print >> sys.stderr, "Number of nodes: {}".format(len(G.nodes()))
  print >> sys.stderr, "Number of walks: {}".format(num_walks)
  print >> sys.stderr, "Data size (walks*length): {}".format(data_size)
  print >> sys.stderr, "Walking..."
   
  walk_files = walks.write_walks_to_disk(
    G, 
    "%s.walks" % args.output,
    num_paths   = args.number_walks,
    path_length = args.walk_length, 
    alpha       = 0, 
    rand        = random.Random(args.seed),
    num_workers = args.workers
  )


def main():
  parser = ArgumentParser("deepwalk",
                          formatter_class=ArgumentDefaultsHelpFormatter,
                          conflict_handler='resolve')
  
  parser.add_argument('--format', default='adjlist',
                      help='File format of input file')

  parser.add_argument('--input', nargs='?', required=True,
                      help='Input graph file')

  parser.add_argument("-l", "--log", dest="log", default="INFO",
                      help="log verbosity level")

  parser.add_argument('--number-walks', default=10, type=int,
                      help='Number of random walks to start at each node')

  parser.add_argument('--output', required=True,
                      help='Output representation file')

  parser.add_argument('--representation-size', default=64, type=int,
                      help='Number of latent dimensions to learn for each node.')

  parser.add_argument('--seed', default=0, type=int,
                      help='Seed for random walk generator.')

  parser.add_argument('--undirected', default=True, type=bool,
                      help='Treat graph as undirected.')

  parser.add_argument('--walk-length', default=40, type=int,
                      help='Length of the random walk started at each node')

  parser.add_argument('--window-size', default=5, type=int,
                      help='Window size of skipgram model.')

  parser.add_argument('--workers', default=1, type=int,
                      help='Number of parallel processes.')


  args = parser.parse_args()
  numeric_level = getattr(logging, args.log.upper(), None)
  logging.basicConfig(format=LOGFORMAT)
  logger.setLevel(numeric_level)
  
  process(args)

if __name__ == "__main__":
  sys.exit(main())
