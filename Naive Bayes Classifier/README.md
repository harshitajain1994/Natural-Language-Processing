The aim of this project is to do authorship identification on lines of poetry written by Emily Bronte and William Shakespeare. We’ll be using the Na ̈ıve Bayes classifier provided by nltk. 

* maketsv.py : This is a convenience script for converting the provided data into a form that is suitable for the classifier.  
* classify.py : This is an implementation of a Naive Bayes classifier that uses NLTK’s Naive Bayes code. It generates features from train- ing data, evaluates on a small percentage of the training data, then re-trains on the full training data and generates predictions for the test data. It is implemented with a baseline feature set  
