import sys
sys.path.insert(0, '..\models\LDA')
import LdaEs

def topic_train(article):
	#print article
	LdaEs.main(article)

if __name__ == "__main__":
	topic_train(article)