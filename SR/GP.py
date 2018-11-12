from random import random,randint,choice
from copy import deepcopy
from math import log
from StringIO import StringIO
from google.appengine.ext import db
import sys
import os

final_output=""

class fwrapper:
	def __init__(self,function,childcount,name):
		self.function=function
		self.childcount=childcount
		self.name=name
		
class node:
	def __init__(self,fw,children):
		self.function=fw.function
		self.name=fw.name
		self.children=children
	def evaluate(self,inp):
		results=[n.evaluate(inp) for n in self.children]
		return self.function(results)
	def display(self,indent=0):
		global final_output
		final_output+=(' '*indent)+self.name+"\n"
		for c in self.children:
			c.display(indent+1)	
		
class paramnode:
	def __init__(self,idx):
		self.idx=idx
	def evaluate(self,inp):
		return inp[self.idx]
	def display(self,indent=0):
		global final_output
		final_output+='%sp%d' % (' '*indent,self.idx)+"\n"		
		
class constnode:
	def __init__(self,v):
		self.v=v
	def evaluate(self,inp):
		return self.v
	def display(self,indent=0):
		global final_output
		final_output+='%s%d' % (' '*indent,self.v)+"\n"	
		
addw=fwrapper(lambda l:l[0]+l[1],2,'add')
subw=fwrapper(lambda l:l[0]-l[1],2,'subtract')
mulw=fwrapper(lambda l:l[0]*l[1],2,'multiply')

def iffunc(l):
	if l[0]>0: return l[1]
	else: return l[2]
ifw=fwrapper(iffunc,3,'if')

def isgreater(l):
	if l[0]>l[1]: return 1
	else: return 0
gtw=fwrapper(isgreater,2,'isgreater')

flist=[addw,mulw,ifw,gtw,subw]		

def exampletree( ):
	return node(ifw,[
					node(gtw,[paramnode(0),constnode(3)]),
					node(addw,[paramnode(1),constnode(5)]),
					node(subw,[paramnode(1),constnode(2)]),
					]
				)

def makerandomtree(pc,maxdepth=4,fpr=0.5,ppr=0.6):
	if random( )<fpr and maxdepth>0:
		f=choice(flist)
		children=[makerandomtree(pc,maxdepth-1,fpr,ppr)
			for i in range(f.childcount)]
		return node(f,children)
	elif random( )<ppr:
		return paramnode(randint(0,pc-1))
	else:
		return constnode(randint(0,10))	

def hiddenfunction():
	return x**2+5	

def buildhiddenset(func):
	rows=[]
	count=0
	y_exists=func.find('y')
	table=""
	if y_exists==-1:
		table=' <table style="border-collapse:collapse;border:1px solid black;width:250px">\
				<caption>Randomly Genereated Dataset</caption>\
				<tr align="left">\
					<th style="border:1px solid black;padding:20px">X</th>\
					<th style="border:1px solid black;padding:20px">Output</th>\
				</tr>'
	else:
		table=' <table style="border-collapse:collapse;border:1px solid black;width:280px">\
				<caption>Randomly Genereated Dataset</caption>\
				<tr align="left">\
					<th style="border:1px solid black;padding:20px">X</th>\
					<th style="border:1px solid black;padding:20px">Y</th>\
					<th style="border:1px solid black;padding:20px">Output</th>\
				</tr>'
		
	for i in range(200):
		x=randint(0,40)
		y=randint(0,40)
		hidden_func=func.replace("x",str(x)).replace("y",str(y))
		val_func=eval(hidden_func)
		rows.append([x,y,val_func])
		if count<5:
			if y_exists==-1:
				table+='<tr align="left"><td style="border:1px solid black;padding:20px">' \
				+ str(x) + '</td><td style="border:1px solid black;padding:20px">' \
				+ str(val_func) + '</td></tr>'
			else:
				table+='<tr align="left"><td style="border:1px solid black;padding:20px">' \
				+ str(x) + '</td><td style="border:1px solid black;padding:20px">' \
				+ str(y) + '</td><td style="border:1px solid black;padding:20px">' \
				+ str(val_func) + '</td></tr>'
			count=count+1
	table+='</table>'
	global final_output
	final_output=""
	final_output+= "<h2><center>We've received the following output from our program: </center></h2><br/>"
	final_output+= "<h4>Hidden function:  "+ func + "</h4><br/>"
	final_output+=table+'</br>'
	return rows	
	
def scorefunction(tree,s):
	dif=0
	for data in s:
		v=tree.evaluate([data[0],data[1]])
		dif+=abs(v-data[2])
	return dif	
	
def mutate(t,pc,probchange=0.1):
	if random( )<probchange:
		return makerandomtree(pc)
	else:
		result=deepcopy(t)
		if isinstance(t,node):
			result.children=[mutate(c,pc,probchange) for c in t.children]
		return result	
		
def crossover(t1,t2,probswap=0.7,top=1):
	if random( )<probswap and not top:
		return deepcopy(t2)
	else:
		result=deepcopy(t1)
		if isinstance(t1,node) and isinstance(t2,node):
			result.children=[crossover(c,choice(t2.children),probswap,0)
							for c in t1.children]
		return result

def evolve(func,pc,popsize,rankfunction,maxgen=500,
			mutationrate=0.1,breedingrate=0.4,pexp=0.7,pnew=0.05):
	# Returns a random number, tending towards lower numbers. The lower pexp
	# is, more lower numbers you will get
	def selectindex( ):
		return int(log(random( ))/log(pexp))
	
	# Create a random initial population
	population=[makerandomtree(pc) for i in range(popsize)]
	global final_output
	final_output+= "<pre><b>The fitness values in each iteration are:</b>\n"
	final_output+= ('-'*40) +"\n"
	for i in range(maxgen):
		scores=rankfunction(population)
		final_output+=str(scores[0][0])+"\n"
		if scores[0][0]==0: 
			final_output+= "\n"+ ('-'*40) +"\n"
			final_output+= "\n<b>The automatically generated function is:-</b>"
			final_output+= "\n"+ ('-'*40) +"\n"
			break
	
		# The two best always make it
		newpop=[scores[0][1],scores[1][1]]		
	
		# Build the next generation
		while len(newpop)<popsize:
			if random( )>pnew:
				newpop.append(mutate(
							crossover(scores[selectindex( )][1],
									scores[selectindex( )][1],
									probswap=breedingrate),
									pc,probchange=mutationrate))
			else:
			# Add a random node to mix things up
				newpop.append(makerandomtree(pc))
		population=newpop
	scores[0][1].display( )
	final_output+= "\n"+ ('-'*40) +"\n</pre>"
	return scores[0][1]

def getrankfunction(dataset):
	def rankfunction(population):
		scores=[(scorefunction(t,dataset),t) for t in population]
		scores.sort( )
		return scores
	return rankfunction

class dbResult(db.Model):
	funcname=db.StringProperty(required=True)
	result=db.TextProperty(required=True)
	
def getgenfunction(func,refresh):
	global final_output
	func_name=func.replace("**","power").replace("*","mul").replace("+","plus").replace("-","minus")
	
	q = db.GqlQuery("SELECT * FROM dbResult " +
                    "WHERE funcname = :1",
					func_name)
					
	form='<form action="/' +func+ '" method="post">\
		  <input value="Real-time Calculation" type="submit" /> \
		  </form>'
		  
	if(not refresh and q.count()>0):
		return populateResult(func_name)+'<br/><center>' +form+ '</center><br/>'	
	else:	
		rf=getrankfunction(buildhiddenset(func))
		evolve(func,2,500,rf,mutationrate=0.2,breedingrate=0.1,pexp=0.7,pnew=0.1)
		output="<h2><i><center>Real-time Result</center></i></h2><br/>"+final_output+populateResult(func_name)
		dbR=dbResult(funcname=func_name,result=final_output)
		dbR.put()
		return output

def populateResult(func_name):
	q = db.GqlQuery("SELECT * FROM dbResult " +
                    "WHERE funcname = :1",
					func_name)
	if(q.count()>0):				
		temp="<br/><h2><i><center>Cached Copy</center></i></h2><br/>"
		count=1
		for p in q.run():
			temp=temp+p.result.replace("We've","<h4>"+str(count)+".</h4> "+"   We've")	
			count=count+1
		return temp	
	else:
		return ""
	
