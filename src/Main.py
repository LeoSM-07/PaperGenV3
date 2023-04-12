from PaperGen import paper_gen

with open('./input/message.txt', 'r') as f:
    textFile = f.read().strip().split('\n')

paper_gen(textFile, 0, "")
print("Done!")