import requests
import ollama
import json

SEARXNG_URL = "http://localhost:8080/search" # change it to your own 
MAX_SEARCH = 5

def searchWeb(question):
    params = {
        "q": question,
        "format": "json"
    }

    try:
        response = requests.get(SEARXNG_URL, params=params)

        web_data = response.json()

        formatted_results = []

        for result in web_data["results"][:MAX_SEARCH]:
            formatted_results.append({
                "title": result["title"],
                "content": result["content"],
                "url": result["url"]
            })
        return formatted_results

    except requests.exceptions.RequestException as e:
        print(f"Search Failed: {e}")

def askAI(question, search_results, total_message):
    web_content = ""
    full_response = ""

    for result in search_results:
        web_content += (f"Title: {result['title']} Content: {result['content']} URL: {result['url']} \n")


    stream = ollama.chat(
        model="gemma3",
        messages=total_message+[{"role": "user", "content": f"Given the question {question} answer it based on the search result {web_content} and use the past messages"}],
        stream=True
    )

    print("AI: ")

    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
        full_response += chunk["message"]["content"]
    print("\n")

    return full_response

messages = []

print("Chat started! Type 'quit' to exit.\n")

while True:
    user_question = input("User: ")
    print("\n")

    if user_question.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    result = searchWeb(user_question)

    messages.append({"role": "user", "content": user_question})

    response = askAI(user_question, result, messages)
    
    messages.append({"role": "assistant", "content": response})
