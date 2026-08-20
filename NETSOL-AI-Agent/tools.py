import httplib2
import google_auth_httplib2
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from googleapiclient.discovery import build
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_community import CalendarToolkit, GmailToolkit
from langchain_google_community.calendar.utils import (
    build_calendar_service,
    get_google_credentials,
)

from langchain_google_community.gmail.utils import (
    build_resource_service as build_gmail_service,
)
# from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv(override=True)

tavily = TavilySearch(max_results=2)

#Google search
@tool
def google_search(query: str):
    """This function is used to do the google search"""
    print("\n*************GOOGLE SEARCH*************")
    result = tavily.invoke(query)
    return result

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# embeddings = GoogleGenerativeAIEmbeddings(
#     model="gemini-embedding-2-preview",
#     output_dimensionality=1536
# )

vectorstore = FAISS.load_local(
    "my_utils/my_faiss_db",
    embeddings,
    allow_dangerous_deserialization=True
)


#rag
@tool
def rag_retrieval(query: str):
    """Search the company knowledge base and return relevant information."""
    print("\n*************RAG*************")

    results = vectorstore.similarity_search_with_score(query, k=3)

    filtered = [
        doc.page_content
        for doc, score in results
        # if score < 0.5
    ]

    print("\n\nRAG RESULT  :", filtered)
    return "\n\n---\n\n".join(filtered) if filtered else "No relevant context found."




# Get credentials (your existing function)
credentials = get_google_credentials(
    token_file="token.json",
    scopes=[
        "https://www.googleapis.com/auth/calendar",
        "https://mail.google.com/",
    ],
    client_secrets_file="credentials.json",
)

# # Fresh HTTP client per request
# def create_fresh_calendar_service():
#     """Build service with fresh httplib2 session every time"""
#     http = httplib2.Http(timeout=90)  # fresh object
#     authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=http)
#     return build("calendar", "v3", http=authorized_http)

# # Create toolkit normally
# calendar_toolkit = CalendarToolkit(credentials=credentials)
# tools = calendar_toolkit.get_tools()

calendar_resource = build_calendar_service(credentials=credentials)
gmail_resource = build_gmail_service(credentials=credentials)
calendar_toolkit = CalendarToolkit(api_resource=calendar_resource)
gmail_toolkit = GmailToolkit(api_resource=gmail_resource)
tools = calendar_toolkit.get_tools() + gmail_toolkit.get_tools()