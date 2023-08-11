from ray.job_submission import JobSubmissionClient, JobStatus
import time


def submit_job():
    # If using a remote cluster, replace 127.0.0.1 with the head node's IP address.
    client = JobSubmissionClient("http://127.0.0.1:8265")
    job_id = client.submit_job(
        # Entrypoint shell command to execute
        entrypoint="python script.py",
        # Path to the local directory that contains the script.py file
        runtime_env={"working_dir": "./",
                     "py_modules": ["/Users/parthparmar/github/shannon/python/shannon"],
                     "pip": ["aiosignal==1.3.1",
                             "annotated-types==0.5.0",
                             "anyio==3.7.1",
                             "argilla==1.12.0",
                             "attrs==23.1.0",
                             "backoff==2.2.1",
                             "certifi==2023.5.7",
                             "cffi==1.15.1",
                             "chardet==5.1.0",
                             "charset-normalizer==3.1.0",
                             "click==8.1.4",
                             "commonmark==0.9.1",
                             "cryptography==41.0.1",
                             "Deprecated==1.2.14",
                             "et-xmlfile==1.1.0",
                             "exceptiongroup==1.1.2",
                             "filelock==3.12.2",
                             "filetype==1.2.0",
                             "frozenlist==1.3.3",
                             "fsspec==2023.6.0",
                             "grpcio==1.49.1",
                             "h11==0.14.0",
                             "httpcore==0.16.3",
                             "httpx==0.23.3",
                             "huggingface-hub==0.16.2",
                             "idna==3.4",
                             "iniconfig==2.0.0",
                             "Jinja2==3.1.2",
                             "joblib==1.3.1",
                             "jsonschema==4.18.0",
                             "jsonschema-specifications==2023.6.1",
                             "lxml==4.9.3",
                             "Markdown==3.4.3",
                             "MarkupSafe==2.1.3",
                             "mccabe==0.6.1",
                             "monotonic==1.6",
                             "mpmath==1.3.0",
                             "msg-parser==1.2.0",
                             "msgpack==1.0.5",
                             "networkx==3.1",
                             "nltk==3.8.1",
                             "numpy==1.23.5",
                             "olefile==0.46",
                             "openpyxl==3.1.2",
                             "opensearch-py==2.2.0",
                             "packaging==23.1",
                             "pandas==1.5.3",
                             "pdf2image==1.16.3",
                             "pdfminer.six==20221105",
                             "Pillow==10.0.0",
                             "pluggy==1.2.0",
                             "protobuf==3.20.*",
                             "pyarrow==12.0.1",
                             "pycodestyle==2.8.0",
                             "pycparser==2.21",
                             "pydantic==1.10.11",
                             "pydantic_core==2.1.2",
                             "pyflakes==2.4.0",
                             "Pygments==2.15.1",
                             "pypandoc==1.11",
                             "pypdf==3.12.1",
                             "python-dateutil==2.8.2",
                             "python-docx==0.8.11",
                             "python-magic==0.4.27",
                             "python-pptx==0.6.21",
                             "pytz==2023.3",
                             "PyYAML==6.0",
                             "referencing==0.29.1",
                             "regex==2023.6.3",
                             "requests==2.31.0",
                             "rfc3986==1.5.0",
                             "rich==13.0.1",
                             "rpds-py==0.8.8",
                             "safetensors==0.3.1",
                             "scikit-learn==1.3.0",
                             "scipy==1.11.1",
                             "sentence-transformers==2.2.2",
                             "sentencepiece==0.1.99",
                             "six==1.16.0",
                             "sniffio==1.3.0",
                             "sympy==1.12",
                             "tabulate==0.9.0",
                             "threadpoolctl==3.1.0",
                             "tokenizers==0.13.3",
                             "tomli==2.0.1",
                             "torch==2.0.1",
                             "torchvision==0.15.2",
                             "tqdm==4.65.0",
                             "transformers==4.30.2",
                             "typer==0.7.0",
                             "typing_extensions==4.7.1",
                             "unstructured==0.7.12",
                             "urllib3==1.26.16",
                             "wrapt==1.14.1",
                             "xlrd==2.0.1",
                             "XlsxWriter==3.1.2"]}
    )
    print(job_id)

    def wait_until_status(job_id, status_to_wait_for, timeout_seconds=300):
        start = time.time()
        while time.time() - start <= timeout_seconds:
            status = client.get_job_status(job_id)
            print(f"status: {status}")
            if status in status_to_wait_for:
                break
            time.sleep(1)

    wait_until_status(job_id, {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED})
    logs = client.get_job_logs(job_id)
    print(logs)


if __name__ == '__main__':
    submit_job()
