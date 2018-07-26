
import sys
import re
from porterStemmer import PorterStemmer
from collections import defaultdict
from array import array
import gc
import math

porter=PorterStemmer()

class CreateIndex:

    def __init__(self):
        self.index=defaultdict(list)    #the inverted index
        self.titleIndex={}
        self.tf=defaultdict(list)          #term frequencies of terms in documents
                                                    #documents in the same order as in the main index
        self.df=defaultdict(int)         #document frequencies of terms in the corpus
        self.wordall=defaultdict(int)
        self.numDocuments=0

    
    def getStopwords(self):
        '''get stopwords from the stopwords file'''
        f=open(self.stopwordsFile, 'r')
        # f1=open(self.wordfile,'w')
        stopwords=[line.rstrip() for line in f]
        for stop in stopwords :
        	self.wordall[stop]+=1
        self.sw=dict.fromkeys(stopwords)
        f.close()
        # f1.close()
        

    def getTerms(self, line):
        '''given a stream of text, get the terms from the text'''
        line=line.lower()
        line=line.split('\n')
        term=[]
        for i,aline in enumerate(line):
            aline=re.sub(r'[^a-z0-9 ]',' ',aline) #put spaces instead of non-alphanumeric characters
            aline=aline.rstrip()
            words=aline.split()
            for word in words:
            	if word not in self.sw:
            		term.append([word,i])     
        # term=[x for x in term if x[0] not in self.sw]  #eliminate the stopwords
        for word in term:
            self.wordall[word[0]]+=1
        term=[ [porter.stem(word[0], 0, len(word[0])-1),word[1]] for word in term]
        return term

    def parseCollection(self):
        ''' returns the id, title and text of the next page in the collection '''
        doc=[]
        for line in self.collFile:
            if line=='</page>\n':
                break
            doc.append(line)
        
        curPage=''.join(doc)
        pageid=re.search('<id>(.*?)</id>', curPage, re.DOTALL)
        pagetitle=re.search('<title>(.*?)</title>', curPage, re.DOTALL)
        pagetext=re.search('<text>(.*?)</text>', curPage, re.DOTALL)
        
        if pageid==None or pagetitle==None or pagetext==None:
            return {}

        d={}
        d['id']=pageid.group(1)
        d['title']=pagetitle.group(1)
        d['text']=pagetext.group(1)

        return d


    def writeIndexToFile(self):
        '''write the index to the file'''
        #write main inverted index
        f=open(self.indexFile, 'w')
        # f1=open(self.wordfile,'w')
        #first line is the number of documents
        print >>f, self.numDocuments
        self.numDocuments=float(self.numDocuments)
        for term in self.index.iterkeys():
            # print >> f1, term
            postinglist=[]
            for p in self.index[term]:
            	# print term
                docID=p[0]
                positions=p[1]
                wordposition=[]
                for position in positions:
                	position[0]=str(position[0])
                	position[1]=str(position[1])
                	wordposition.append('/'.join(position)) 
                # postinglist.append(':'.join([str(docID) ,','.join(map(str,str(['-'.join(map(str,position))] for position in positions)))]))
                postinglist.append(':'.join([str(docID) ,','.join(map(str,wordposition))]))
            #print data
            postingData=';'.join(postinglist)
            tfData=','.join(map(str,self.tf[term]))
            idfData='%.4f' % math.log(self.numDocuments/self.df[term])
            print >> f, '|'.join((term, postingData, tfData, idfData))
        f.close()
        f=open(self.wordfile,'w')
        for term in self.wordall.iterkeys():
            print >> f, term
        # f1.close()
        f.close()
        
        #write title index
        f=open(self.titleIndexFile,'w')
        for pageid, title in self.titleIndex.iteritems():
            print >> f, pageid, title
        f.close()
        

    def getParams(self):
        '''get the parameters stopwords file, collection file, and the output index file'''
        param=sys.argv
        self.stopwordsFile=param[1]
        self.collectionFile=param[2]
        self.indexFile=param[3]
        self.titleIndexFile=param[4]
        self.wordfile=param[5]
        

    def createIndex(self):
        '''main of the program, creates the index'''
        self.getParams()
        self.collFile=open(self.collectionFile,'r')
        self.getStopwords()
                
        #bug in python garbage collector!
        #appending to list becomes O(N) instead of O(1) as the size grows if gc is enabled.
        gc.disable()
        
        pagedict={}
        pagedict=self.parseCollection()
        #main loop creating the index
        while pagedict != {}:                    
            lines='\n'.join((pagedict['title'],pagedict['text']))
            pageid=int(pagedict['id'])
            terms=self.getTerms(lines)
            # alllines=self.getLines(lines)
            
            self.titleIndex[pagedict['id']]=pagedict['title']
            
            self.numDocuments+=1
            
            #build the index for the current page
            termdictPage={}
            for position, term in enumerate(terms):
            	# print term
                try:
                    termdictPage[term[0]][1].append([position,term[1]])
          
                except:
                    termdictPage[term[0]]=[pageid, [[position,term[1]]]]
            
            #normalize the document vector
            norm=0
            for term, posting in termdictPage.iteritems():
                norm+=len(posting[1])**2
            norm=math.sqrt(norm)
            
            #calculate the tf and df weights
            for term, posting in termdictPage.iteritems():
                self.tf[term].append('%.4f' % (len(posting[1])/norm))
                self.df[term]+=1
            
            #merge the current page index with the main index
            for termPage, postingPage in termdictPage.iteritems():
            	# print postingPage
                self.index[termPage].append(postingPage)
            
            # for termPage, postingPage in termlinedictPage.iteritems():
            #     self.wordline[termPage].append(postingPage) 

            pagedict=self.parseCollection()


        gc.enable()
            
        self.writeIndexToFile()
        
    
if __name__=="__main__":
    c=CreateIndex()
    c.createIndex()
    

