# from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_groq import ChatGroq
# from langchain_chroma import Chroma
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from .structure_outputs import *
# from .prompts import *

# class Agents():
#     def __init__(self):
#         # Choose which LLMs to use for each agent (GPT-4o, Gemini, LLAMA3,...)
#         llama = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
#         gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
        
#         # QA assistant chat
#         embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
#         vectorstore = Chroma(persist_directory="db", embedding_function=embeddings)
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

#         # Categorize email chain
#         email_category_prompt = PromptTemplate(
#             template=CATEGORIZE_EMAIL_PROMPT, 
#             input_variables=["email"]
#         )
#         self.categorize_email = (
#             email_category_prompt | 
#             llama.with_structured_output(CategorizeEmailOutput)
#         )

#         # Used to design queries for RAG retrieval
#         generate_query_prompt = PromptTemplate(
#             template=GENERATE_RAG_QUERIES_PROMPT, 
#             input_variables=["email"]
#         )
#         self.design_rag_queries = (
#             generate_query_prompt | 
#             llama.with_structured_output(RAGQueriesOutput)
#         )
        
#         # Generate answer to queries using RAG
#         qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_PROMPT)
#         self.generate_rag_answer = (
#             {"context": retriever, "question": RunnablePassthrough()}
#             | qa_prompt
#             | llama
#             | StrOutputParser()
#         )

#         # Used to write a draft email based on category and related informations
#         writer_prompt = ChatPromptTemplate.from_messages(
#             [
#                 ("system", EMAIL_WRITER_PROMPT),
#                 MessagesPlaceholder("history"),
#                 ("human", "{email_information}")
#             ]
#         )
#         self.email_writer = (
#             writer_prompt | 
#             llama.with_structured_output(WriterOutput)
#         )

#         # Verify the generated email
#         proofreader_prompt = PromptTemplate(
#             template=EMAIL_PROOFREADER_PROMPT, 
#             input_variables=["initial_email", "generated_email"]
#         )
#         self.email_proofreader = (
#             proofreader_prompt | 
#             llama.with_structured_output(ProofReaderOutput) 
#         )

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
##CHANGE MADE##
# We keep ChatGroq because the RAG agent (which is text-only) can still use it for speed.
from langchain_groq import ChatGroq
##CHANGE MADE##
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .structure_outputs import *
from .prompts import *
##CHANGE MADE##
# We add this import to handle multimodal messages
from langchain_core.messages import HumanMessage
##CHANGE MADE##

class Agents():
    def __init__(self):
        # Choose which LLMs to use for each agent (GPT-4o, Gemini, LLAMA3,...)
        ##CHANGE MADE##
        # Llama is still here for our text-only RAG agent
        llama = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
        # Gemini will be used for all email-processing (multimodal) agents
        # Use a supported model name. 'gemini-pro-vision' is not available
        # for the v1beta generative API (causes 404). Fall back to a known
        # available model like 'gemini-1.5-flash' (adjust if your account
        # has different permitted models).
        # Use deterministic, low-temperature generation for classification and structured output
        gemini = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.0)
        ##CHANGE MADE##
        
        # QA assistant chat
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectorstore = Chroma(persist_directory="db", embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        ##CHANGE MADE##
        # We are modifying all agents that read the email.
        # They will now use the multimodal 'gemini' model.
        # The prompt is removed from the chain here because it will be
        # constructed as a complex HumanMessage (text + images) in the node.
        self.categorize_email = (
            gemini.with_structured_output(CategorizeEmailOutput)
        )
        ##CHANGE MADE##

        ##CHANGE MADE##
        # This agent also needs to see the attachments, so it must use 'gemini'.
        self.design_rag_queries = (
            gemini.with_structured_output(RAGQueriesOutput)
        )
        ##CHANGE MADE##
        
        # Generate answer to queries using RAG
        # This agent is TEXT-ONLY. It answers a text query based on retrieved text.
        # We can leave it as 'llama' for speed.
        qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_PROMPT)
        self.generate_rag_answer = (
            {"context": retriever, "question": RunnablePassthrough()}
            | qa_prompt
            | llama
            | StrOutputParser()
        )

        ##CHANGE MADE##
        # This agent must also be 'gemini' to see the email and attachments.
        # We remove the PromptTemplate and just pass the model.
        # The node will be responsible for formatting the [system, history, human] messages.
        self.email_writer = (
            gemini.with_structured_output(WriterOutput)
        )
        ##CHANGE MADE##

        ##CHANGE MADE##
        # This agent must also be 'gemini' to see the email and attachments.
        self.email_proofreader = (
            gemini.with_structured_output(ProofReaderOutput) 
        )
        ##CHANGE MADE##
