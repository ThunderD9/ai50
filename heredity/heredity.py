import csv
import itertools
from mailbox import ExternalClashError
from re import M, T
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    Probability = 1

    for human in people:
        if human in one_gene:  # Checking the number of genes a person have
            genes = 1
        elif human in two_genes:
            genes = 2
        else:
            genes = 0
        if human in have_trait:  # Checking if a person has the trait
            trait = True
        else:
            trait = False

        prob_of_gene = PROBS['gene'][genes]  # Caluclating the probabilty of having that gene
        prob_of_trait = PROBS['trait'][genes][trait]  # Caluclating the probabilty of having that trait

        if people[human]["father"] is None:  # Checking whether the parents are registered
            Probability *= prob_of_gene * prob_of_trait
        else:  # If parents are registered
            mom = people[human]["mother"]
            dad = people[human]["father"]
            percentage_of = {}

            for parents in [mom, dad]:
                if parents in one_gene:  # Caluclating the probability of the parents genes 
                    percentage = (0.5 * (1 - PROBS['mutation'])) + (0.5 * PROBS['mutation'])
                elif parents in two_genes:
                    percentage = 1 - PROBS['mutation']
                else:
                    percentage = 0 + PROBS['mutation'] 
                percentage_of[parents] = percentage  # Stores the probability of parents

            if genes == 0:  # Caluclating the pb given the parents percentage
                Probability *= (1 - percentage_of[mom]) * (1 - percentage_of[dad])
            elif genes == 1:
                Probability *= (1 - percentage_of[mom]) * percentage_of[dad] + percentage_of[mom] * (1 - percentage_of[dad])
            else:
                Probability *= percentage_of[mom] * percentage_of[dad]

            Probability *= prob_of_trait
    return Probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for human in probabilities:  
        if human in one_gene:
            genes = 1
        elif human in two_genes:
            genes = 2
        else:
            genes = 0  # Checking the genes of a person
        
        probabilities[human]["gene"][genes] = probabilities[human]["gene"][genes] + p

        if human in have_trait:  # Checking the trait of a person
            trait = True
        else:
            trait = False
        probabilities[human]["trait"][trait] = probabilities[human]["trait"][trait] + p  # Adds the new joint probability


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    normal = probabilities.copy()
    for human in probabilities:
        for type in ['gene', 'trait']:
            sum_total = sum(probabilities[human][type].values())
            for category in probabilities[human][type]:
                val = probabilities[human][type][category]
                normalized_value = val / sum_total
                normal[human][type][category] = normalized_value  # Noramlizes the distribution's value
    return normal


if __name__ == "__main__":
    main()