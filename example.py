# MIT License
# 
# Copyright (c) 2019 Cong Feng
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Examples."""
from rouge import rouge_n_sentence_level
from rouge import rouge_l_sentence_level
from rouge import rouge_n_summary_level
from rouge import rouge_l_summary_level
from rouge import rouge_w_sentence_level
from rouge import rouge_w_summary_level

if __name__ == '__main__':
    # The use of sentence level rouges.
    reference_sentence = 'the police killed the gunman'.split()
    summary_sentence = 'the gunman police killed'.split()

    print('Sentence level:')
    score = rouge_n_sentence_level(summary_sentence, reference_sentence, 1)
    print('ROUGE-1: %f' % score.f1_measure)

    _, _, rouge_2 = rouge_n_sentence_level(summary_sentence, reference_sentence, 2)
    print('ROUGE-2: %f' % rouge_2)

    _, _, rouge_l = rouge_l_sentence_level(summary_sentence, reference_sentence)
    print('ROUGE-L: %f' % rouge_l)

    _, _, rouge_w = rouge_w_sentence_level(summary_sentence, reference_sentence)
    print('ROUGE-W: %f' % rouge_w)

    # The use of summary level rouges.
    # Each summary is a list of sentences.
    reference_sentences = [
        'The gunman was shot dead by the police before more people got hurt'.split(),
        'This tragedy causes lives of five , the gunman included'.split(),
        'The motivation of the gunman remains unclear'.split(),
    ]

    summary_sentences = [
        'Police killed the gunman . no more people got hurt'.split(),
        'Five people got killed including the gunman'.split(),
        'It is unclear why the gunman killed people'.split(),
    ]

    print('Summary level:')
    _, _, rouge_1 = rouge_n_summary_level(summary_sentences, reference_sentences, 1)
    print('ROUGE-1: %f' % rouge_1)

    _, _, rouge_2 = rouge_n_summary_level(summary_sentences, reference_sentences, 2)
    print('ROUGE-2: %f' % rouge_2)

    _, _, rouge_l = rouge_l_summary_level(summary_sentences, reference_sentences)
    print('ROUGE-L: %f' % rouge_l)

    _, _, rouge_w = rouge_w_summary_level(summary_sentences, reference_sentences)
    print('ROUGE-W: %f' % rouge_w)
