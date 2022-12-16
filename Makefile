#################### PACKAGE ACTIONS ###################

run:
	streamlit run app.py

# ----------------------------------
#              INSTALL
# ----------------------------------

install_requirements:
	@pip install -r requirements.txt

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
