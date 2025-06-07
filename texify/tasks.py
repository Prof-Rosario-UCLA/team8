from manager import celery_app
import subprocess
import tempfile
import os

@celery_app.task(bind=True, max_retries=3, track_started=True)
def compile_latex_to_pdf(self, latex_code: str) -> str:
    try:
        print("Compiling...")
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, "document.tex")
            pdf_path = os.path.join(tmpdir, "document.pdf")

            # Write the LaTeX source to a .tex file
            with open(tex_path, "w") as f:
                f.write(latex_code)

            # Compile using pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                raise RuntimeError("LaTeX compilation failed")

            with open(pdf_path, "rb") as pdf_file:
                return pdf_file.read().hex()  # return PDF as hex string

    except Exception as exc:
        print("Retrying...")
        raise self.retry(exc=exc, countdown=5)
