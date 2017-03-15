import sys
sys.path.insert(0, '..\models\LDA')
import GetTopics

def topic_load(article):
	#print article
	return GetTopics.main(article)

if __name__ == "__main__":
	topic_load()