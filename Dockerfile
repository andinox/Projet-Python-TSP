FROM python:3.12.7

WORKDIR /app
COPY . /app

RUN pip install django
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "DiagnosticTool/manage.py", "runserver", "0.0.0.0:8000"]