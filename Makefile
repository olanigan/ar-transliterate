install:
	pip install -r requirements.txt

run:
	streamlit run app2.py

clean:
	rm -rf __pycache__
	rm -rf .streamlit
