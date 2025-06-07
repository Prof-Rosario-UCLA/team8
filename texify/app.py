from flask import Flask
from tasks import compile_latex_to_pdf

app = Flask(__name__)

with open("../samples/resume.tex", "r") as file:
    latex_code = file.read()

@app.get('/ping')
def ping():
    return 'Pong'

@app.post('/compile')
def compile():
    task = compile_latex_to_pdf.delay(latex_code)
    print(task)
    return {
        'task_id': task.id
    }

@app.get('/status/<task_id>')
def status(task_id: str):
    task = compile_latex_to_pdf.AsyncResult(task_id)
    print(task)
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "FAILURE":
        return {"status": "failure", "error": str(task.result)}
    elif task.state == "SUCCESS":
        return {"status": "done", "pdf_hex": task.result}
    else:
        return {"status": task.state}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='9090')
