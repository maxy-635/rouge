# Copyright 2019 Cong Feng. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
Yet another Python implementation of ROUGE.
"""

import collections
import itertools
import math

__all__ = [
    "rouge_n_sentence_level",
    "rouge_l_sentence_level",
    "rouge_l_summary_level",
    "rouge_n_summary_level",
]

DEFAULT_WEIGHT_FACTOR = 1.2


def _num_ngrams(words, n):
    """
    Return the number of nth gram of words.

    >>> _num_ngrams([1, 2, 3], 3)
    1
    >>> _num_ngrams([1, 2, 3], 2)
    2

    :param words: a list of tokens.
    :param n: int.
    :return: number of n-gram.
    """
    return max(len(words) - n + 1, 0)


def _get_ngram(words, n):
    """
    Return a generator on all nth grams of words.

    >>> list(_get_ngram([1, 2, 3], 2))
    [(1, 2), (2, 3)]
    >>> list(_get_ngram([1, 2, 3], 1))
    [(1,), (2,), (3,)]

    :param words: a list of tokens.
    :param n: int.
    :return: a generator
    """
    for i in range(_num_ngrams(words, n)):
        n_gram = words[i:i + n]
        yield tuple(n_gram)


def _count_ngrams(words, n):
    """
    Collect nth gram of words into a Counter.

    >>> _count_ngrams([1, 1, 2, 2], 2)
    Counter({(1, 1): 1, (1, 2): 1, (2, 2): 1})
    >>> _count_ngrams([1, 2, 3], 2)
    Counter({(1, 2): 1, (2, 3): 1})

    :param words: a list of tokens.
    :param n: N for ngrams.
    :return: a Counter.
    """
    return collections.Counter(_get_ngram(words, n))


def _divide_or_zero(numerator, denominator):
    """
    Divide numerator by denominator. If the latter is 0, return 0.

    >>> _divide_or_zero(1, 2)
    0.5
    >>> _divide_or_zero(1, 0)
    0.0

    :param numerator: float.
    :param denominator: float.
    :return: float.
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _compute_f1_measure(recall, precision, alpha=None):
    if alpha is None:
        alpha = 0.5
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be between [0, 1]")
    return _divide_or_zero(precision * recall, (1 - alpha) * precision + alpha * recall)


def _f1_measure(numerator, r_denominator, p_denominator, alpha=None):
    """
    Compute a weighted F-measure.

    Effectively given by:
        Recall = numerator / r_p_denominator
        Precision = numerator / p_denominator
        F1_Measure = Recall * Precision / (alpha * Recall + 1 - alpha) * Precision)

    >>> _f1_measure(1, 2, 3, 0.5)
    (0.5, 0.3333333333333333, 0.4)

    >>> _f1_measure(1, 0, 1, 0.5)
    (0.0, 1.0, 0.0)

    :param numerator: 
    :param r_denominator: 
    :param p_denominator: 
    :param alpha: the weighting factor.
    :return: 3-tuple of recall, precision and f1.
    :raise ValueError: If alpha is not between [0, 1].
    """
    recall = _divide_or_zero(numerator, r_denominator)
    precision = _divide_or_zero(numerator, p_denominator)
    f1 = _compute_f1_measure(recall, precision, alpha)
    return recall, precision, f1


def _clipped_ngram_count(summary_ngrams, reference_ngrams):
    """
    For each instance of ngram that appear in both summary_ngrams and reference_ngrams,
    first clip their count by taking minimum value. Then sum up the clipped counts.

    >>> from collections import Counter
    >>> summary_ngrams = Counter('the police killed the gunman'.split())
    >>> summary_ngrams
    Counter({'the': 2, 'police': 1, 'killed': 1, 'gunman': 1})
    >>> reference_ngrams = Counter('gunman the police killed'.split())
    >>> reference_ngrams
    Counter({'gunman': 1, 'the': 1, 'police': 1, 'killed': 1})
    >>> summary_ngrams & reference_ngrams
    Counter({'the': 1, 'police': 1, 'killed': 1, 'gunman': 1})
    >>> _clipped_ngram_count(summary_ngrams, reference_ngrams)
    4

    :param summary_ngrams: a Counter.
    :param reference_ngrams: a Counter
    :return: the clipped count.
    """
    overlap = summary_ngrams & reference_ngrams
    return sum(overlap.values())


def rouge_n_sentence_level(summary_sentence, reference_sentence, n, alpha=None):
    """
    Calculate ROUGE-N on sentence level.

    :param summary_sentence: a sentence.
    :param reference_sentence: a sentence.
    :param n: n for ngram.
    :param alpha: weight on the recall (default 0.5).
    :return: a 3-tuple, recall, precision and f1 measure.
    """
    summary_ngrams = _count_ngrams(summary_sentence, n)
    reference_ngrams = _count_ngrams(reference_sentence, n)
    total_matches = _clipped_ngram_count(summary_ngrams, reference_ngrams)

    recall_denominator = _num_ngrams(reference_sentence, n)
    precision_denominator = _num_ngrams(summary_sentence, n)
    return _f1_measure(total_matches, recall_denominator, precision_denominator, alpha)


def _flatten_sentences(sentences):
    """
    Flatten a list of sentences into a concatenated list of tokens.
    Adapted from https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists.

    >>> s1 = 'the gunman kill police'.split()
    >>> s2 = 'police killed the gunman'.split()
    >>> _flatten_sentences([s1, s2])
    ['the', 'gunman', 'kill', 'police', 'police', 'killed', 'the', 'gunman']

    :param sentences: a list of sentences.
    :return: a list of tokens.
    """
    return list(itertools.chain.from_iterable(sentences))


def rouge_n_summary_level(summary_sentences, reference_sentences, n, alpha=None):
    """
    Calculate summary level ROUGE-N.
    The sentences are first flatten and then feed to rouge_n_sentence_level.
    :param summary_sentences: a list of sentences.
    :param reference_sentences: a list of sentences.
    :param n: n for ngram.
    :param alpha: weight on the recall (default 0.5).
    :return: a 3-tuple, recall, precision and f1 measure.
    """
    summary_sentences = _flatten_sentences(summary_sentences)
    reference_sentences = _flatten_sentences(reference_sentences)

    return rouge_n_sentence_level(summary_sentences, reference_sentences, n, alpha)


def _lcs_length(x, y):
    """
    Compute the length of the Longest Common Subsequence between sequences x
    and y.
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    >>> _lcs_length('ABCDE', 'CD')
    2
    >>> _lcs_length('the police killed the gunman'.split(), 'gunman police killed'.split())
    2

    :param x: sequence of words
    :param y: sequence of words
    :return: Length of LCS between x and y
    """
    n, m = len(x), len(y)

    def _compute_lcs_table():
        """
        Computes the length of the longest common subsequence (lcs) between two
        strings. The implementation below uses a DP programming algorithm and runs
        in O(nm) time where n = len(x) and m = len(y).
        Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

        :param x: collection of words
        :param y: collection of words
        :return Table of dictionary of coord.
        """
        len_table = {}
        for i in range(n + 1):
            for j in range(m + 1):
                if i == 0 or j == 0:
                    len_table[i, j] = 0
                elif x[i - 1] == y[j - 1]:
                    len_table[i, j] = len_table[i - 1, j - 1] + 1
                else:
                    len_table[i, j] = max(len_table[i - 1, j], len_table[i, j - 1])
        return len_table

    table = _compute_lcs_table()
    return table[n, m]


def rouge_l_sentence_level(summary_sentence, reference_sentence, alpha=None):
    """
    Calculate sentence level ROUGE-L.

    :param summary_sentence: a sentence.
    :param reference_sentence: a sentence.
    :param alpha: weight on the recall (default 0.5).
    :return: a 3-tuple, recall, precision and f1 measure.
    """
    lcs_length = _lcs_length(summary_sentence, reference_sentence)
    r_denominator = len(reference_sentence)
    p_denominator = len(summary_sentence)
    return _f1_measure(lcs_length, r_denominator, p_denominator, alpha)


def _lcs_elements(x, y):
    """
    Compute the index pairs that make up a LCS of x and y.
    Return a set of 2-tuple, t. t[0] and t[1] are indices drawn from x, y respectively.
    The actual sequence can be constructed from this set, given all the indices to the value
    known.

    >>> _lcs_elements('ab', 'bc')
    {(1, 0)}
    >>> _lcs_elements('a', 'd')
    set()
    >>> _lcs_elements('abc', 'abc')
    {(0, 0), (1, 1), (2, 2)}

    :param x: a sequence.
    :param y: a sequence.
    :return: a set.
    """

    def _compute_lcs_table():
        """
        Compute the length table and trace table for the LCS problem of x and y.
        From the length table one can get the len of LCS.
        From the trace table one can get the actual sequence and the indices of each element
        from both x and y.

        The function is so factored that we don't need to compute the elements of a LCS when
        we only need its length. In `rouge_l_sentence_level`, only the len is needed since we
        don't perform any union operation. In `rouge_l_summary_level`, the elements are needed
        and more computation is spent on it.

        :param x: a sequence.
        :param y: a sequence.
        :return len_table, trace_table.
        """
        n, m = len(x), len(y)
        len_table = {}
        trace_table = {}
        for i in range(n + 1):
            for j in range(m + 1):
                if i == 0 or j == 0:
                    # Initialize the tables are we do the loop.
                    # This saves us dedicated init code at the cost of some performance.
                    len_table[i, j] = 0
                elif x[i - 1] == y[j - 1]:
                    len_table[i, j] = len_table[i - 1, j - 1] + 1
                    trace_table[i, j] = 'd'  # go diagonal.
                elif len_table[i - 1, j] > len_table[i, j - 1]:
                    len_table[i, j] = len_table[i - 1, j]
                    trace_table[i, j] = 'u'  # go up.
                else:
                    len_table[i, j] = len_table[i, j - 1]
                    trace_table[i, j] = 'l'  # go left.
        return trace_table

    i, j = len(x), len(y)
    elements = set()

    table = _compute_lcs_table()
    while i != 0 and j != 0:
        if table[i, j] == 'd':
            i -= 1
            j -= 1
            elements.add((i, j))
        elif table[i, j] == 'u':
            i -= 1
        else:
            j -= 1
    return elements


def _make_lcs_union(summary_sentences, reference_sentence):
    """
    Returns LCS_u(r_i, C) which is the union longest common subsequence between
    reference sentence ri and candidate summary C.

    For example if
        r_i = w1 w2 w3 w4 w5
        c1 = w1 w2 w6 w7 w8
        c2 = w1 w3 w8 w9 w5
    then:
        LCS(r_i, c1) = "w1 w2"
        LCS(r_i, c2) = "w1 w3 w5"
    and:
        LCS_u(r_i, C) = "w1 w2 w3 w5"

    >>> r_i = 'w1 w2 w3 w4 w5'.split()
    >>> c1 = 'w1 w2 w6 w7 w8'.split()
    >>> c2 = 'w1 w3 w8 w8 w5'.split()

    >>> union = _make_lcs_union([c1, c2], r_i)
    >>> union
    {0, 1, 2, 4}
    >>> [r_i[idx] for idx in union]
    ['w1', 'w2', 'w3', 'w5']

    :param summary_sentences: a list of sentences.
    :param reference_sentence: a sentence.
    :return: a set whose element is the indices of words of reference_sentence.
    """
    lcs_union = set()
    for sentence in summary_sentences:
        lcs = _lcs_elements(sentence, reference_sentence)
        lcs_union = lcs_union.union(ref_idx for _, ref_idx in lcs)
    return lcs_union


def _flatten_and_count_ngrams(sentences, n):
    """
    First flatten a list of sentences, then count ngrams on it.

    >>> s1 = 'the cat sat on the mat'.split()
    >>> s2 = 'the cat on the mat'.split()
    >>> _flatten_and_count_ngrams([s1, s2], 1)
    Counter({('the',): 4, ('cat',): 2, ('on',): 2, ('mat',): 2, ('sat',): 1})

    :param sentences: a list of sentences.
    :param n: N for ngrams.
    :return: Counter.
    """
    return _count_ngrams(_flatten_sentences(sentences), n)


def rouge_l_summary_level(summary_sentences, reference_sentences, alpha=None):
    """
    Calculate the summary level ROUGE-L.
    :param summary_sentences: a list of sentence.
    :param reference_sentences: a list of sentence.
    :param alpha: weight on the recall (default 0.5).
    :return: a 3-tuple, recall, precision and f1 measure.
    """
    summary_unigrams = _flatten_and_count_ngrams(summary_sentences, 1)
    reference_unigrams = _flatten_and_count_ngrams(reference_sentences, 1)

    total_lcs_words = 0
    for reference in reference_sentences:
        lcs_union = _make_lcs_union(summary_sentences, reference)
        for word in lcs_union:
            unigram = (reference[word],)
            if (unigram in summary_unigrams and unigram in reference_unigrams
                    and summary_unigrams[unigram] > 0 and reference_unigrams[unigram] > 0):
                summary_unigrams[unigram] -= 1
                reference_unigrams[unigram] -= 1
                total_lcs_words += 1

    r_denominator = sum(len(sentence) for sentence in reference_sentences)
    p_denominator = sum(len(sentence) for sentence in summary_sentences)
    return _f1_measure(total_lcs_words, r_denominator, p_denominator, alpha)


def _weight_fn(x, weight=None, inverse=False):
    """

    :param x:
    :param weight:
    :param inverse:
    :return:
    """
    if weight is None:
        weight = DEFAULT_WEIGHT_FACTOR
    if not weight > 1.0:
        raise ValueError('weight must be > 1.0')
    if inverse:
        weight = 1 / weight
    return math.pow(x, weight)


def _lcs_length_with_weight(x, y, weight=None):
    """
    Compute the weighted LCS length.
    :param x: a sequence.
    :param y: a sequence.
    :param weight: the weight factor passed to the weight function.
    :return: float.
    """
    weighted_len = {}
    consecutive_match = {}
    m, n = len(x), len(y)
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:  # Corner case.
                weighted_len[i, j] = 0
                consecutive_match[i, j] = 0
            elif x[i - 1] == y[j - 1]:
                k = consecutive_match[i - 1, j - 1]
                update = _weight_fn(k + 1, weight) - _weight_fn(k, weight)
                weighted_len[i, j] = weighted_len[i - 1, j - 1] + update
                consecutive_match[i, j] = k + 1
            else:
                weighted_len[i, j] = max(weighted_len[i - 1, j], weighted_len[i, j - 1])
                consecutive_match[i, j] = 0
    return weighted_len[m, n]


def rouge_w_sentence_level(summary_sentence, reference_sentence, weight=None, alpha=None):
    """

    :param summary_sentence:
    :param reference_sentence:
    :param weight:
    :param alpha:
    :return:
    """
    def compute(n, d):
        return _weight_fn(
            _divide_or_zero(n, _weight_fn(d, weight=weight)),
            inverse=True,
            weight=weight
        )

    numerator = _lcs_length_with_weight(summary_sentence, reference_sentence, weight)
    recall = compute(numerator, len(reference_sentence))
    precision = compute(numerator, len(summary_sentence))
    f1 = _compute_f1_measure(recall, precision, alpha)
    return recall, precision, f1


def rouge_w_summary_level(summary_sentences, reference_sentences, weight=None, alpha=None):
    """

    :param summary_sentences:
    :param reference_sentences:
    :param weight:
    :param alpha:
    :return:
    """
    pass
