format:
	bin/black main.py
	bin/mypy main.py

run:
	./main.py

install-dependencies:
	python3 -m pip install -r requirements.txt
