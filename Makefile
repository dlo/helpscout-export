format:
	bin/black main.py
	bin/mypy main.py

download:
	./main.py download

import:
	./main.py import

install-dependencies:
	python3 -m venv .
	bin/python3 -m pip install -r requirements.txt

generate-er-diagram:
	# https://www.schemacrawler.com/diagramming.html
	docker run --mount type=bind,source="$(pwd)",target=/home/schcrwlr --rm -it schemacrawler/schemacrawler /opt/schemacrawler/bin/schemacrawler.sh --server=sqlite --database=helpscout.db --info-level=standard --command script --script-language python --script mermaid.py
