from flask import Flask, request
from tasks import compile_latex_to_pdf

app = Flask(__name__)


@app.get("/ping")
def ping():
    return "Pong"


@app.post("/compile")
def compile():
    data = request.get_json()
    if not data.get("template") or not data.get("data"):
        return {"error": "Missing template or data."}
    task = compile_latex_to_pdf.delay(data.get("template"), data.get("data"))
    return {"task_id": task.id}


@app.get("/status/<task_id>")
def status(task_id: str):
    task = compile_latex_to_pdf.AsyncResult(task_id)
    # Note that celery returns PENDING even if the task_id is not known
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "FAILURE":
        return {"status": "failure", "error": str(task.result)}
    elif task.state == "SUCCESS":
        return {"status": "done", "url": task.result}
    else:
        return {"status": task.state}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="9090")
