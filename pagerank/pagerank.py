import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    probability_dist = {}

    dictonary_len = len(corpus.keys())  # Check if any of the pages has any outgoing links
    page_len = len(corpus[page])

    if len(corpus[page]) < 1:
        for x in corpus.keys():  # If there are no no outgoing pages it will randomly chose from all possible pages
            probability_dist[x] = 1 / dictonary_len

    else:
        randomness = (1 - damping_factor) / dictonary_len  # Caluculates distribution for outgoing pages
        event = damping_factor / page_len

        for y in corpus.keys():
            if y not in corpus[page]:
                probability_dist[y] = randomness
            else:
                probability_dist[y] = event + randomness

    return probability_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    s_dict = corpus.copy()
    for i in s_dict:  # Prepares a dictionary witth zero samples
        s_dict[i] = 0
    sample = None  

    for a in range(n):
        if sample:  # If a previous sample is available this will choose using transition model
            d = transition_model(corpus, sample, damping_factor)
            d_list = list(d.keys())
            d_weights = [d[i] for i in d]
            sample = random.choices(d_list, d_weights, k=1)[0]
        else:
            sample = random.choice(list(corpus.keys()))  # If there is no previous sample, it will choose randomly

        s_dict[sample] += 1  # This counts each sample

    for i in s_dict:
        s_dict[i] /= n  # This turns samples counts to percentages

    return s_dict  # Returns the page rank values


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    no_of_pages = len(corpus)
    old_dictionary = {}
    new_dictionary = {}  # Declaring two new dictionarys

    for page in corpus:
        old_dictionary[page] = 1 / no_of_pages # Giving each page a rank of 1/n, n = no.of in corpus

    while True:  # Repeatedly calculating new rank values basing on all of the current rank values
        for page in corpus:
            rank = 0
            for link_page in corpus:
                if page in corpus[link_page]:  # Checking if page has links to our page
                    rank += (old_dictionary[link_page] / len(corpus[link_page]))  # Caluculates if our page has the same links as other pages, 2nd part of the formula
                if len(corpus[link_page]) == 0:  # if page has no links we take it as having one link for every other page
                    rank += (old_dictionary[link_page]) / len(corpus)
            rank *= damping_factor
            rank += (1 - damping_factor) / no_of_pages  # First part of the formula

            new_dictionary[page] = rank

        difference = max([abs(new_dictionary[y] - old_dictionary[y]) for y in old_dictionary])
        if difference < 0.001:  # Checks if the difference is minimal
            break
        else:
            old_dictionary = new_dictionary.copy()

    return old_dictionary

if __name__ == "__main__":
    main()