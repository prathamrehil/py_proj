from __future__ import print_function

from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner, StrictGlobalSequenceAligner
import re, json
import spacy

def align_sequence(reference_sentence, check_sentence):
    # Create sequences to be aligned.
    a = Sequence(reference_sentence.split())
    b = Sequence(check_sentence.split())

    # Create a vocabulary and encode the sequences.
    v = Vocabulary()
    aEncoded = v.encodeSequence(a)
    bEncoded = v.encodeSequence(b)

    # Create a scoring and align the sequences using global aligner.
    scoring = SimpleScoring(5, -5)
    # aligner = GlobalSequenceAligner(scoring, 2)
    aligner = StrictGlobalSequenceAligner(scoring, 2)

    score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

    # Iterate over optimal alignments and print them.
    for encoded in encodeds:
        alignment = v.decodeSequenceAlignment(encoded)
        # print(alignment)
        # print('Alignment score:', alignment.score)
        break 
    
    return alignment

#####################################################
def evaluate_sequence(reference_sentence:list, check_sentence:list):
    
    nlp = spacy.load('en_core_web_md')
    
    final_sq1 = []
    final_sq2 = []
    flag = False
    sub_flag = False
    
    def add_ele(index):
        final_sq1.append(reference_sentence[index])
        final_sq2.append(check_sentence[index])
    
    for i in range(0, len(reference_sentence)):
        doc1 = nlp(reference_sentence[i])
        doc2 = nlp(check_sentence[i])
        
        if doc1.text == "-" :
            if flag:
                add_ele(i-1)
            else:
                flag = True
            continue
            
        if len(doc1) != len(doc2) and flag != True:
            # Consider as different
            add_ele(i)

        elif (len(doc1)>1 or len(doc2)>1) and flag != True:
            for z in range(len(doc1)):
                if doc1.text[z] != doc2.text[z]:
                    # Not same. Hence add as different!
                    add_ele(i)

                    sub_flag = True
                    break
            
            if not sub_flag:
                # Same: All items in doc match
                add_ele(i)
            sub_flag = False

        else:
            if doc1.text == doc2.text or doc1[0].lemma_ == doc2[0].lemma_:
                # Acceptable(same text)
                add_ele(i)

            else:                        
                if flag == True:
                    add_ele(i-1)
                    flag = False
                    
                add_ele(i)

                
    return final_sq1, final_sq2
    
# s1 = "Ram and Sita went home at 5pm after a jog. They started jogging at 2pm and were jogging at 10km per hour. How far did they jog?"
# s2 = "Ram and Sita went home at 5pm, after a jog. They started jogging at 2pm and were jogging at 10km per hour. How far did they jog?"
# l1, l2 = align_sequence(s1, s2)
# f1, f2 = evaluate_sequence(l1, l2)

# print(f1)
# print(f2)

#####################################################

def get_markdown(tokens1, tokens2):
    def bold(token):
        return f"__{token}__"
    
    def strike_through(token):
        return f"~{token}~"
    
    md = ""
    for i in range(len(tokens1)):
        if tokens1[i] == tokens2[i]:
            md += tokens1[i] + " "
        
        if tokens1[i] == "-" and tokens2[i] != "-":
            md += bold(tokens2[i]) + " "
            
        if tokens2[i] == "-" and tokens1[i] != "-":
            md += strike_through(tokens1[i]) + " "

        else:
            md += tokens1[i] + " "
    return md

def get_html(tokens1, tokens2):
    def highlight(token):
        return f"<mark>{token}</mark>"
    
    def strike_through(token):
        return f"<s>{token}</s>"
    
    ht = ""
    for i in range(len(tokens1)):
        if tokens1[i] == tokens2[i]:
            ht += tokens1[i] + " "
        
        elif tokens1[i] == "-" and tokens2[i] != "-":
            ht += highlight(tokens2[i]) + " "
            
        elif tokens2[i] == "-" and tokens1[i] != "-":
            ht += strike_through(tokens1[i]) + " "
            
        else:
            ht += tokens1[i] + " "
        
    return ht
# input =  ['A', 'table', 'weighs', '13', '-', 'kgs.', 'A', 'chair', 'weighs', '-', '-', '7kgs.', 'What', 'would', 'be', 'the', 'overall', 'weight', 'of', 'a', 'dining', 'set', 'which', 'consists', 'of', '1', 'table', 'and', '4', 'chairs?']
# corrected = ['A', 'table', 'weighs', '13', 'kg.', '-', 'A', 'chair', 'weighs', '7', 'kg.', '-', 'What', 'would', 'be', 'the', 'overall', 'weight', 'of', 'a', 'dining', 'set', 'which', 'consists', 'of', '1', 'table', 'and', '4', 'chairs?']
# print(get_markdown(input, corrected))













'''
# Declare are different
        if len(doc1) != len(doc2):
        
        # Same text in both list
        if doc1[i].text == doc2[i].text :
            final_sq1.append(doc1[i].text)
            final_sq2.append(doc2[i].text)
        
        # If not same: Either an insertion(edit) or deletion
        else: 
            # If hyphen: could be deletion or insertion next
            if doc1[i].text == "-" :
                flag = True
                continue
                
            if doc1[i].lemma_ == doc2[i-1].lemma_:
                print("Merging acceptable change in words:", doc1[i].lemma_)
                final_sq1.append(doc1[i].text)
                final_sq2.append(doc2[i-1].text)
                
            else:
                print("Different lemmas. Not merging words!")
                if flag == True:
                    final_sq1.append(doc1[i-1].text)
                    final_sq2.append(doc2[i-1].text)
                    flag = False
                final_sq1.append(doc1[i].text)
                final_sq2.append(doc2[i].text)
'''