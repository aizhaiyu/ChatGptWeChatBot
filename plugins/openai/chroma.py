
from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("docs/车辆管理系统.pdf")
documents  = loader.load()
print(documents[0])

from langchain.text_splitter import CharacterTextSplitter
 
#创建分割器
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)
 
#分割文档
docs = text_splitter.split_documents(documents)
print(docs)