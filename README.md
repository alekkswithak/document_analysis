# Document Analysis
Django app to view words and sentences taken from various documents, can be viewed all together or by document.

## Requirements
* Python 3.x
* Spacy

## Setup
From the root directory:
Create a new venv and install the requirements
```
pip install -r requirements.txt
```
Download Spacy's models
```
python -m spacy download en_core_web_sm
```
From the directory containing manage.py:
```
python manage.py makemigrations word_sentences
python manage.py migrate
```
To run the tests:
```
python manage.py test word_sentences
```
To run the analyser on the sample documents and populate the db:
(takes up to 3 minutes)
```
python manage.py read_eigen
```
Finally, run the project:
```
python manage.py runserver
```

## Usage
Once the server is running, the root url takes you to the list of all words, paginated by 12.
Click the sentences button to reveal the sentences for each word.
Click download under the page heading to download all data as txt.

In the navbar click on Documents to view a list of all documents.
Click Browse Words to view word data specific to that document.
Click download under the page heading to download document specific data as txt.

## To do
> Word search field
> Document upload capability
> Word detail page
> API (because everyone wants an API)
> Better front end
> Improve saving speed
