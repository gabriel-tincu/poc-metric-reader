FROM python:3.7
RUN mkdir app
WORKDIR app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD *.py /app/
ADD *.sql /app/
CMD ["python", "-m", "unittest"]