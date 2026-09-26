load:
	python src/etl/loader.py

test:
	pytest tests/

clean:
	rm -rf __pycache__
	