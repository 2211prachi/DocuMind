def run_pipeline(query, thread_id):
    state = {
        "question": query,
        "messages": [],
        "route": "",
        "retrieved": "",
        "answer": "",
        "eval_retries": 0
    }

    # memory node
    state["messages"].append(query)

    # router node (simple logic)
    if "time" in query.lower():
        state["route"] = "tool"
    else:
        state["route"] = "retrieve"

    # retrieval node
    if state["route"] == "retrieve":
        docs = retrieve_docs(query)
        state["retrieved"] = docs
    else:
        state["retrieved"] = []

    # answer node
    answer = generate_answer(query, state["retrieved"], state["messages"])
    state["answer"] = answer

    return state