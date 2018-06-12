import nltk
import re
import time
import PyPDF2
import sqlite3
import sys
from nltk.corpus import stopwords
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.sparse.csr import csr_matrix
from sklearn.feature_extraction import text
from pandas import DataFrame



reload(sys)  
sys.setdefaultencoding('utf8')
#creating a database
conn=sqlite3.connect('Internship.db')
conn.text_factory = str 
c=conn.cursor()
#creating a table named keywords_and_weightages
c.execute("""CREATE TABLE IF NOT EXISTS keywords_and_weightages(keyword TEXT, weight REAL)""")



#Lemmatising words
class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, Text):
        return [self.wnl.lemmatize(t) for t in nltk.word_tokenize(Text)]

#function to extract text from pdfs
def getTextFromPdf():

	pdfFile=open('JavaBasics-notes.pdf','rb')

	pdfReader = PyPDF2.PdfFileReader(pdfFile)
	

	#prints total number of pages in pfd. In our case, it is 23.
	x=pdfReader.numPages
	
	print(x)


	#Get complete text from pdf page by page.
	lines=[]
	for i in range(x):
		pageObj = pdfReader.getPage(i)
		#print(pageObj.extractText())
		page = pageObj.extractText()
		#an array of strings called page
		
		lines.append(page)
	#getting training data
	f = open('training.txt', "r")
	lines2 = f.readlines()
	f.close()
	#print(lines)
	
	
	return lines,lines2

# cleaning and training data
def removeUnwanted_provideWeightage(Text,Text2):
	
	#improving the stop words set
	own_stop= set(('ok','ha','reserved.java','reserved.java basic','right','right reserved.java','basicsjava basic','basicsjava','c','d','e','f','g','t','``','basics jguru.com','java basicsjava','java basics','jguru.com','jguru.com right','--','=','b','\'s','\'d','\'re','**a','*/all','*/b','*/int',"''",'~',',','..','>','<','-1','-2','-3','-4','-5','-6','-7','-8','-9','-10''=','//','/**','...','>=','<=','0','1','2','3','4','5','6','7','8','9','10', '10 1996','15expressionsmost','jGuru.com','$',';','//','*/','/*','**','%','',"'",'\\t','&','& &','"','^','*', '-','+','.','www','!', '! !', '! &', "! ''", '! (', '! )', '! *', '! +', '! --', '! <', '! =', '! ==', '! ?', '! ^', '! ``', 'www browser', 'www programmingthe', 'youmust', 'youmust specifically', 'youoverride', 'youoverride default', 'yourbrowser', 'yourbrowser window', 'zero-extend', 'zero-extend right-shift', '{', '{ (', '{ /**', '{ //', '{ 1', '{ ;', '{ case', '{ data', '{ public', '{ return', '{ stats', '{ t', '|', '| !', '|=note', '|=note precedence', '||', '|| !', '}', '} (', '} ,', '} ;', 'All', 'Rights', 'Reserved.Java','//depot/main/src/edu/modules/JavaBasics/javaBasics.mml','{','}','#','@','(',')','[',']', ':', '!','-23This', 'page', 'intentionally', 'left', 'blank','1996-2003','Reserved'))
	#adding into the stopwords list of scikit-learn
	stop_words = text.ENGLISH_STOP_WORDS.union(own_stop)
	#initialising lemmatizer
	lemmatizer = WordNetLemmatizer()
	
	
	#creating a tfidfVectorizer
	tfidf_vect = TfidfVectorizer(tokenizer=LemmaTokenizer(),token_pattern="(?i)\b[a-z]+\b",stop_words=stop_words,ngram_range=(1,2))
	X = tfidf_vect.fit(Text)
	
	features=tfidf_vect.transform(Text2)
	print(features.shape)
	feature=features.toarray()
	

	#creating two lists, one for keywords and another for weights.
	i=0
	words=[]
	tfidf_val=[]
	for w in sorted(tfidf_vect.vocabulary_, key=tfidf_vect.vocabulary_.get):
  		#print w, tfidf_vect.vocabulary_[w]
  		#print(tfidf_value1111[-(tfidf_vect.vocabulary_[w])])
  		words.append(w)
  		if w=='java'or w=='JavaBasics'or w=='Portability'or w=='Security'or w=='variable'or w=='Robustness'or w=='javaapplications'or w=='C/C++'or w=='ProgramStructure'or w=='program'or w=='applet'or w=='Comments'or w=='objects'or w=='strings'or w=='arrays'or w=='int'or w=='generic' or w=='classes' or w=='Classes':
  			tfidf_val.append((tfidf_vect.idf_[tfidf_vect.vocabulary_[w]])*0.1)
  		
  		else:
  			tfidf_val.append((tfidf_vect.idf_[tfidf_vect.vocabulary_[w]]))
  		
  		i+=1


  	
  	#print(len(words))
  	#print(len(tfidf_val))
  	#Selecting the top keywords
  	fin_words=[]
  	fin_val=[]
  	for j in range(len(words)):
  		if tfidf_val[j]<=2.7:
  			fin_words.append(words[j])
  			fin_val.append(tfidf_val[j])
  			

  
  	fin_words.append('secure')
  	fin_words.append('robust')
  	fin_val.append(1.8976)
  	fin_val.append(1.76589)

  	#printing the keywords list
  	print(len(fin_val))
  	print(len(fin_words))

  	#printing the length of keywords list
  	for j in range(len(fin_words)):
  		print(fin_words[j])
  		print(fin_val[j])



	return fin_words, fin_val


#insert keywords and their respective weights into a database and excel sheet
def Insert_into_Database(fin_words,fin_val):

	for i in range(len(fin_val)):
		c.execute("INSERT INTO keywords_and_weightages(keyword, weight) VALUES(?,?)",
			(fin_words[i], fin_val[i]))
	#committimg te changes into the table
	conn.commit()

	#creating the pandas dataframe
	df = DataFrame({'KEYWORDS': fin_words, 'WEIGHTS': fin_val})
	#inserting into an Excel Sheet
	df.to_excel('test.xlsx', sheet_name='sheet1', index=False)



Text,Text2=getTextFromPdf()
#print(Text2)
fin_words, fin_val=removeUnwanted_provideWeightage(Text,Text2)

Insert_into_Database(fin_words,fin_val)

