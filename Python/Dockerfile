FROM python
ENV PATH /usr/src/app/bin:$PATH
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt  

COPY bin/* ./
CMD python review-scraper.py