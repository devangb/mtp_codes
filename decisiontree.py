class decisionnode:
	def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
		self.col=col
		self.value=value
		self.results=results
		self.tb=tb
		self.fb=fb

#Divides the rows into true and false set based upon the value(value) in column(column) for rows(rows)
def divideset(rows,column,value):
	#If row is in first set(true) or second set(false)
	split_function=None
	if isinstance(value,int) or isinstance(value,float):
		split_function = lambda row:row[column]>=value
	else:
		split_function = lambda row:row[column]==value

	#Divide rows into two sets
	set1=[row for row in rows if split_function(row)]
	set2=[row for row in rows if not split_function(row)]
	return (set1,set2)

#Give out number of possible result and results dictionary
def uniquecounts(rows):
	results={}
	for row in rows:
		#Classifying column is assumed to be last column
		r=row[len(row)-1]
		if r not in results:
			results[r]=0
		results[r]+=1
	return results

#Probability that a randomly placed item will be in wrong category
#Higher the value worse the split
def giniimpurity(rows):
	total=len(rows)
	counts=uniquecounts(rows)
	imp=0
	for k1 in counts:
		p1 = float(counts[k1])/total
		for k2 in counts:
			if k1!=k2:
				p2 = float(counts[k2])/total
				imp += p1*p2
	return imp

#Entropy function used is sum of p(x)log(p(x))
#p(i) = frequency(outcome) = count(outcome)/count(total rows)
def entropy(rows):
	from math import log
	log2 = lambda x:log(x)/log(2)
	results = uniquecounts(rows)
	ent = 0.0
	for r in results.keys():
		p=float(results[r])/len(rows)
		ent = ent-p*log2(p)
	return ent

#Build tree from training data
def buildtree(rows,scoref=entropy):
	if len(rows)==0: return decisionnode()
	current_score=scoref(rows)

	#Best criteria
	best_gain=0.0
	best_criteria=None
	best_sets=None

	column_count = len(rows[0])-1
	for col in range(0,column_count):
		#Different possible values in that col
		column_values={}
		for row in rows:
			column_values[row[col]]=1
		#Dividing rows for each value
		for value in column_values.keys():
			(set1,set2) = divideset(rows,col,value)

			#Information gain
			p=float(len(set1))/len(rows)
			gain=current_score-p*scoref(set1)-(1-p)*scoref(set2)
			if gain>best_gain and len(set1)>0 and len(set2)>0:
				best_gain = gain
				best_criteria = (col,value)
				best_sets = (set1,set2)
			#print best_gain
	#Creating subbranches
	if best_gain>0:
		trueBranch = buildtree(best_sets[0])
		falseBranch = buildtree(best_sets[1])
		return decisionnode(col=best_criteria[0],value=best_criteria[1],tb=trueBranch,fb=falseBranch)
	else:
		return decisionnode(results=uniquecounts(rows))

#Printing tree
def printtree(tree,indent=''):
	if tree.results!=None:
		print str(tree.results)
	else:
		print str(tree.col)+'::'+str(tree.value)+'? '

		print indent+'T->',
		printtree(tree.tb,indent+' ')
		print indent+'F->',
		printtree(tree.fb,indent+' ')


def getwidth(tree):
  if tree.tb==None and tree.fb==None: return 1
  return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):
  if tree.tb==None and tree.fb==None: return 0
  return max(getdepth(tree.tb),getdepth(tree.fb))+1


from PIL import Image,ImageDraw

def drawtree(tree,jpeg='tree.jpg'):
  w=getwidth(tree)*100
  h=getdepth(tree)*100+120

  img=Image.new('RGB',(w,h),(255,255,255))
  draw=ImageDraw.Draw(img)

  drawnode(draw,tree,w/2,20)
  img.save(jpeg,'JPEG')

def drawnode(draw,tree,x,y):
  if tree.results==None:
    # Get the width of each branch
    w1=getwidth(tree.fb)*100
    w2=getwidth(tree.tb)*100

    # Determine the total space required by this node
    left=x-(w1+w2)/2
    right=x+(w1+w2)/2

    # Draw the condition string
    draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))

    # Draw links to the branches
    draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
    draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))

    # Draw the branch nodes
    drawnode(draw,tree.fb,left+w1/2,y+100)
    drawnode(draw,tree.tb,right-w2/2,y+100)
  else:
    txt=' \n'.join(['%s:%d'%v for v in tree.results.items()])
    draw.text((x-20,y),txt,(0,0,0))

def classify(observation,tree):
  if tree.results!=None:
    return tree.results
  else:
    v=observation[tree.col]
    branch=None
    if isinstance(v,int) or isinstance(v,float):
      if v>=tree.value: branch=tree.tb
      else: branch=tree.fb
    else:
      if v==tree.value: branch=tree.tb
      else: branch=tree.fb
    return classify(observation,branch)


def prune(tree,mingain):
  # If the branches aren't leaves, then prune them
  if tree.tb.results==None:
    prune(tree.tb,mingain)
  if tree.fb.results==None:
    prune(tree.fb,mingain)

  # If both the subbranches are now leaves, see if they
  # should merged
  if tree.tb.results!=None and tree.fb.results!=None:
    # Build a combined dataset
    tb,fb=[],[]
    for v,c in tree.tb.results.items():
      tb+=[[v]]*c
    for v,c in tree.fb.results.items():
      fb+=[[v]]*c

    # Test the reduction in entropy
    delta=entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)

    if delta<mingain:
      # Merge the branches
      tree.tb,tree.fb=None,None
      tree.results=uniquecounts(tb+fb)

def variance(rows):
  if len(rows)==0: return 0
  data=[float(row[len(row)-1]) for row in rows]
  mean=sum(data)/len(data)
  variance=sum([(d-mean)**2 for d in data])/len(data)
  return variance


train_data = [map(int, line.split(',')) for line in file('poker-hand-training-true.txt')]

#print train_data

conf_mat = [[0 for i in range(10)] for j in range(10)]
#my_data = load('decision_tree_example.csv')
tree = buildtree(train_data)
test_data = [map(int, line.split(',')) for line in file('poker-hand-testing.txt')]
correct = 0
total = 0
prune(tree,0.98)
for i in test_data:
	real = i.pop()
	pred = classify(i,tree).keys()[0]
	#print pred
	conf_mat[real][pred] = conf_mat[real][pred] + 1
	if real == pred:
		correct = correct + 1
	total = total + 1

#printtree(tree)
print conf_mat
print correct
print total
print float(correct) * 100/float(total)
#drawtree(tree)
