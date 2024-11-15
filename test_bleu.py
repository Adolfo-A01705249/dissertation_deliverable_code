from nltk.translate.bleu_score import sentence_bleu

manual = '''
ip access-list extended list_name
	deny ip any host 65.9.121.32
	permit ip any any
'''

alternative = '''
ip access-list extended list_name
    deny ip 0.0.0.0 255.255.255.255 65.9.121.32 0.0.0.0
    permit ip 0.0.0.0 255.255.255.255 0.0.0.0 255.255.255.255
'''

reference = [
    manual.split()
]

candidate = '''
ip access-list extended deny_all_to_65_9_121_32
 deny ip any 65.9.121.32 0.0.0.0
 permit ip any any
'''.split()

print(f'BLEU score only manual -> {sentence_bleu(reference, candidate)}')
reference.append(alternative.split())
print(f'BLEU score manual + alternative -> {sentence_bleu(reference, candidate)}')