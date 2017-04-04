import sys
sys.path.insert(0, '..\models')
import summarization

def named_entities(article,categories):
	#print article
	NE = summarization.NER(article,categories)
	return NE
	
if __name__ == "__main__":
	named_entities()