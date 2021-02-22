import numpy as np
from flask import Flask, render_template, redirect, url_for, request
#Doctordata

from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfile
import tkinter.filedialog

import speech_recognition as sr
import re
import pandas as pd
from google.cloud import speech_v1p1beta1
import io
import numpy as np
import nltk
from nameparser.parser import HumanName
import smtplib

import argparse
import os,sys
from pydub import AudioSegment
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
import pandas as pd
from nltk.stem.snowball import SnowballStemmer

import os

import sqlite3 
import unicodedata




 # where name is José



from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename
import email
import email.mime.application
 
   





app = Flask(__name__)  



nam=[]
text=""
symp={}
medi=''
advices=''

  
def aac_to_wav():
	folder = '/home/harshmeetsingh/Music/wav/'                #-----------wav folder contains all the files that need to be converted------------------
	for filename in os.listdir(folder):
		infilename = os.path.join(folder,filename)
		if not os.path.isfile(infilename): continue
		oldbase = os.path.splitext(filename)
		newname = infilename.replace('.tmp', '.aac')
		output = os.rename(infilename, newname)
	formats_to_convert = ['.aac']
	for (dirpath, dirnames, filenames) in os.walk("wav/"):
		for filename in filenames:
			if filename.endswith(tuple(formats_to_convert)):
				filepath = dirpath + '/' + filename
				(path, file_extension) = os.path.splitext(filepath)
				file_extension_final = file_extension.replace('.', '')
				try:
					track = AudioSegment.from_file(filepath,file_extension_final)
					wav_filename = filename.replace(file_extension_final, 'wav')
					wav_path = dirpath + '/' + wav_filename
					print('CONVERTING: ' + str(filepath))
					file_handle = track.export(wav_path, format='wav')
					os.remove(filepath)
				except:
					print("ERROR CONVERTING " + str(filepath))
                
                
                
#--------------------------This part of code converts Speech into Text-------------------------------- ------------------------

def speechToTxt(f):
	r=sr.Recognizer()
#with sr.Microphone() as source:
#print("say:")
	filename=f
	s=''
	with sr.AudioFile(filename) as source:
		a=r.record(source)
		text=r.recognize_google(a)
		#print(text)
	return text

#------------------------This part of code helps for extracting symptoms from text----------------------------------------

def symptoms(text):

	df=pd.read_csv("/home/harshmeetsingh/Music/symp.csv")

	symp=list(df["symptoms"])
	mn=[]

	for i in symp:
		if str(i) in text:
		    m=re.search(r"\b{}\b".format(i),text)
		    if(m!=None):
		    	 mn.append(str(i))
	mn=set(mn)
	#print(mn)
	return mn

    

#------------------------This part of code helps for extracting names from text----------------------------------------
def getNames(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1:
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)





#----------------------------This part of code helps for extracting names of medicines ------------------------------------
def med(text):

	df=pd.read_csv("/home/harshmeetsingh/Music/medi.csv")
	n=list(df["tablets"])
	ss=[]
	
	l=re.split(r"\s+",text)
	for i in l:
		if i.capitalize() in n:
			ss.append(i)

	#print("medicines are", *ss)
	return ss


def advice(text):

	set(stopwords.words('english'))
	
	stop_words = set(stopwords.words('english')) 
	word_tokens = word_tokenize(text) 


	advice=''
	if "advice" in word_tokens:
		for i in range(word_tokens.index("advice")+1,len(word_tokens)):
			advice+=word_tokens[i]+' '
	print("\n",advice) 
	    
	filtered_sentence = [] 
	for w in word_tokens: 
	    if w not in stop_words: 
	        filtered_sentence.append(w) 



	#print("\n\nOriginal Sentence \n\n")
	#print(" ".join(word_tokens)) 
	return advice

	
#---------------------sending email--------------------------



def send_email(eemail):
	
	

# save FPDF() class into  
# a variable pdf 
	pdf = FPDF()    
   
# Add a page 
	pdf.add_page() 
   
# set style and size of font  
# that you want in the pdf 
	pdf.set_font("Arial", size = 15) 
  
# open the text file in read mode 
	f=open("/home/harshmeetsingh/Music/pres.txt","r")
  
# insert the texts in pdf 
	for x in f: 
	    pdf.cell(200, 10, txt = x, ln = 1, align = 'C') 
   
# save the pdf with name .pdf 
	pdf.output("pres.pdf")    




#html to include in the body section
	html = """
 
 	prescription
 
	"""

# Creating message.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "patient visited today"
	#msg['From'] = "deathstrokepool30@gmail.com"
#msg['To'] =['shweta812000k@gmail.com','jagwaniaanchal98@gmail.com','hscawesome3008@gmail.com']
 
# The MIME types for text/html
	HTML_Contents = MIMEText(html, 'html')
 
# Adding pptx file attachment
	filename='pres.pdf'
	fo=open(filename,'rb')
	attach = email.mime.application.MIMEApplication(fo.read(),_subtype="pdf")
	fo.close()
	attach.add_header('Content-Disposition','attachment',filename=filename)
 
# Attachment and HTML to body message.
	msg.attach(attach)
	msg.attach(HTML_Contents)
 
 
	with smtplib.SMTP('smtp.gmail.com',587) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()
	
		smtp.login(USERNAME,PASSWORD)
	
		#body="names"+str(nam)+"\n"+"medicines"+str(ss)+"\n"+"symptoms"+str(mn)+"advices"+str(word_tokens)
		#msg=f'subj:{subject}\n{body}'
	
		smtp.sendmail('harshmeetchandhok@gmail.com',[eemail],msg.as_string())
		print("email sent successfully")




































# this part of the code verifies the login credentials

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['nm'] != 'admin' or request.form['pswd'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
        	return redirect(url_for('land'))
        
    return render_template('log.html', error=error)

@app.route('/login')

# this part redirects to the next page after successful login
def land():
	
	return render_template('land.html') 	



@app.route("/submit1",methods=['GET', 'POST'])

def f4():
	if request.method == 'POST':
		f = request.files['file']  
		f.save(f.filename)
		aac_to_wav()
		tex=speechToTxt(f.filename)
		print(tex)
		symp=symptoms(tex)
		print(symp)
		names = getNames(tex)
		for name in names:
			last_first = HumanName(name).last + ', ' + HumanName(name).first
			nam.append(last_first)
		print(nam)
		medi=med(tex)
		print(medi)
		advices=advice(tex)
		print(advices)
		msg="Name: "+str(names)+"\nSymptoms: "+str(symp)+"\nMedicines: "+str(medi)+"\nAdvice: "+str(advices)
		print(msg)
	
		f1=open("/home/harshmeetsingh/Music/pres.txt","w")
		f1.write(msg)
		f1.close()
		print("DONE")
		
		
		return render_template('land.html')


@app.route("/final", methods=['GET', 'POST'])
def send():
	if request.method == 'POST':
		if request.form['email']!='':
			email=request.form['email']
			val=1
			send_email(email)
		else:
			val=0
	return render_template('land.html',val=val)


if __name__ == "__main__":  
	app.run(debug=True)  
 
