from flask import Flask, Response
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.utils.utils import convert_to_secret_str
from langchain_together import ChatTogether

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index_handler():
    with open("index.html", 'r') as file:
        contents = file.read()

        return contents


@app.route('/stream/<slug>', methods=['GET'])
def stream_handler(slug: str):
    with open(f"articles/{slug}.txt", 'r') as file:
        article = file.read()

    prompt = ChatPromptTemplate.from_messages(messages=[
        SystemMessagePromptTemplate.from_template(
            template=
            """You are a writer. You need to write a tone-adjusted hook paragraph. Write a twist for user provided article"""
        ),
        HumanMessagePromptTemplate.from_template('{article}'),
    ])


    secret_api_key = convert_to_secret_str(
        "42a11ce2c1a46b188bf28fbca83a08084a43898045f2c19085167098d8161fd0")
    

    chat = ChatTogether(
        api_key=secret_api_key,
        model="meta-llama/Llama-3-70b-chat-hf",
    )

    chain = ({
        "article": RunnablePassthrough()
    } | prompt | chat | StrOutputParser())

    def generate():
        chunk = ""
        for char in chain.stream({"article_content": article}):
            chunk += char

            if len(chunk) > 50:
                yield chunk
                chunk = ""

    return Response(generate(),
                    content_type='text/plain',
                    mimetype="text/event-stream")


if __name__ == '__main__':
    print("Running web server..")

    app.run(host='0.0.0.0', port=3000)
