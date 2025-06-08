import os
import time
import subprocess
import tempfile

import json
from jinja2 import Environment, FileSystemLoader

from manager import celery_app
from utils import upload_to_gcs


def escape_latex(value):
    """
    Escape LaTeX special characters like %, $, _, etc.
    You can extend this for full LaTeX safety.
    """
    return (
        value.replace("\\", r"\\")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\^{}")
    )


class LatexEnvironment(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _render_with_escaped_context(self, template_name, context):
        def auto_escape(value):
            if type(value) == str:
                return escape_latex(value)
            elif type(value) == list:
                return [auto_escape(v) for v in value]
            elif type(value) == dict:
                return {k: auto_escape(v) for k, v in value.items()}
            else:
                return escape_latex(str(value))

        escaped_context = {k: auto_escape(v) for k, v in context.items()}
        template = self.get_template(template_name)
        return template.render(escaped_context)


@celery_app.task(bind=True, max_retries=0, track_started=True)
def compile_latex_to_pdf(self, template_url: str, data: any) -> str:
    """
    Compiles a LaTeX file to a PDF and uploads contents to
    Google Cloud Storage and returns a URL to Google Cloud Storage.
    """
    try:
        env = LatexEnvironment(
            loader=FileSystemLoader("."),
            comment_start_string="{=",
            comment_end_string="=}",
            autoescape=False,
        )

        new_data = data.copy()

        for section in data.get("sections", []):
            section_name = section.get("name").lower().replace(" ", "_")
            new_data[section_name] = []
            for item in section.get("items", []):
                new_item = item
                if (
                    section_name != "technical_skills"
                    and type(item["description"]) == str
                ):
                    new_item["description"] = item["description"].split("\n")
                new_data[section_name].append(item)
        del new_data["sections"]

        # TODO(bliutech): add support for downloading templates and selecting them
        latex_code = env._render_with_escaped_context("resume.j2", new_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, "document.tex")
            pdf_path = os.path.join(tmpdir, "document.pdf")

            print(tex_path)

            # Write the LaTeX source to a .tex file
            with open(tex_path, "w") as f:
                f.write(latex_code)

            # Compile using pdflatex
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "document.tex",
                ],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"LaTeX compilation failed {result.stderr} {result.stdout}"
                )

            print("Finished compiling")

            return upload_to_gcs(pdf_path, f"{self.request.id}.pdf")

    except Exception as exc:
        print("Retrying...")
        raise self.retry(exc=exc, countdown=5)
