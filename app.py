import os
from flask import Flask, render_template, request, redirect,session, make_response , jsonify,url_for,redirect, abort
#from tmn_tools import *
import time
import sys
import os
from langchain.document_loaders import PyPDFLoader 
from langchain.embeddings import OpenAIEmbeddings 
from langchain.vectorstores import Chroma 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.document_loaders import MathpixPDFLoader
from langchain.document_loaders import UnstructuredPDFLoader
import getpass
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")



app = Flask(__name__, static_url_path='/static')





# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx','jpg','jpeg','png','gif'}

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']





@app.route("/", methods=["POST","GET"])
def basic_slides():
    files = os.listdir('uploads/')
    files= [item for item in files if 'DS_Store' not in item]
    print(files)

    return render_template("queryDoc.html", files=files)
    #return render_template("test.html")







@app.route("/pdfx1", methods = ["POST","GET"])
def pdfx1():
    question = request.form.get('question')
    docChosen = request.form.get("docChosen")

    print(question)
    print(docChosen)
    response = f"You asked: {question}"
    print(response)
    #pdf_path = "./bloodtest.pdf"
    pdf_path = "./uploads/"+docChosen
    #pdf_path = "./test.pdf"

    chroma_db_impl='duckdb+parquet'
  

    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    print(pages[0].page_content)


    embeddings = OpenAIEmbeddings()
    #vectordb = Chroma.from_documents(pages, embedding=embeddings, persist_directory=".")
    vectordb = Chroma.from_documents(pages, embedding=embeddings)
    #vectordb.persist()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    pdf_qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.8) , vectordb.as_retriever(), memory=memory)


    query = question
    print(query)
    result = pdf_qa({"question": query})
    print(result)
    print("Answer:")
    answer = result["answer"]
    print(answer)


     #To cleanup, you can delete the collection
    vectordb.delete_collection()
    #vectordb.persist()
    return(answer)




@app.route('/upload', methods=['POST'])
def uploadx():
    # Check if a file was posted
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'message': 'File uploaded successfully'})
    return jsonify({'message': 'No file part in the request'})





@app.route('/delete', methods=['POST'])
def delete_file():
    filename = request.form['filename']
    print(filename)
    filePath = "./uploads/" + filename
    print(filePath)
    print(11111)

    os.remove(filePath)
    return "File deleted successfully"





  
if __name__ == "__main__":
    app.run(debug=True,  host='0.0.0.0', port = 5002)
    



# @app.route("/rapper",methods = ["POST","GET"])
# def rapper():
#     key = "pub_uhxsmejejtjtltbwfn"
#     secretKey = "pk_51cbec27-a392-488f-a5ef-38a0a0d9b6a2"
#     uberduck_auth = (key, secretKey)
#     import json

#     lyrics = [
#         [
#             "rap cat, hell make you clap",
#             "hes got the hottest beats and the softest fur",
#             "nothing to laugh at",
#             "riding with the rap cat",
#         ]
#         ]

#     bpm = 144
#     lines = len(lyrics[0])
#     API_ADDRESS = "https://api.uberduck.ai/"
#     output = requests.post(
#         "https://api.uberduck.ai/tts/freestyle",
#         json=dict(lyrics=lyrics, lines=lines, bpm=bpm),
#         auth=uberduck_auth,
#     )
#     Audio(output.json()["mix_url"])

#     output = requests.get(
#     "https://api.uberduck.ai/reference-audio/backing-tracks", auth=uberduck_auth
# )
#     print(output.json())