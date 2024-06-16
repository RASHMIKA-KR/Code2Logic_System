import os
import re
import google.generativeai as genai
import chromadb
import shutil
from chromadb import Documents, EmbeddingFunction, Embeddings

os.environ["GEMINI_API_KEY"] = "AIzaSyDIP2mXBZOEbmw40qy5rn0OjXHxBxztAm8"


class GeminiEmbeddingFunction(EmbeddingFunction):

    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError(
                "Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable"
            )
        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model,
                                   content=input,
                                   task_type="retrieval_document",
                                   title=title)["embedding"]


def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def split_text(text: str):
    split_text = re.split('\n \n', text)
    return [i for i in split_text if i != ""]


def create_chroma_db(documents, path, name):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.create_collection(
        name=name, embedding_function=GeminiEmbeddingFunction())
    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))
    return db, name


def load_chroma_collection(path, name):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(
        name=name, embedding_function=GeminiEmbeddingFunction())
    return db


def get_relevant_passage(query, db, n_results):
    passage = db.query(query_texts=[query],
                       n_results=n_results)['documents'][0]
    return passage


def make_rag_prompt(query, relevant_passage):
    escaped = relevant_passage.replace("'", "").replace('"',
                                                        "").replace("\n", " ")
    prompt = (
        """You are a helpful and informative bot that answers questions using text from the reference passage included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it.
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

  ANSWER:
  """).format(query=query, relevant_passage=escaped)
    return prompt


def generate_response(prompt):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(
            "Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable"
        )
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    answer = model.generate_content(prompt)
    return answer.text


def generate_answer(query):

    text = load_text(file_path="templates/src_doc/program.txt")

    text_chunks = split_text(text)

    db, name = create_chroma_db(documents=text_chunks,
                                path="templates/src_doc/db",
                                name="rag_experiment")

    db = load_chroma_collection(path="templates/src_doc/db",
                                name="rag_experiment")

    relevant_text = get_relevant_passage(query, db, n_results=3)

    prompt = make_rag_prompt(query, relevant_passage="".join(relevant_text))

    answer = generate_response(prompt)
    return answer


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:])
    answer = generate_answer(query)
    print(answer)
