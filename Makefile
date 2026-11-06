.PHONY: setup extract build export all refresh crosswalk clean

setup:      ## install dependencies
	pip install -r requirements.txt

extract:    ## download (cached) every source and land bronze Parquet
	python -m pipeline extract

build:      ## dbt seeds + SQL and Python models + data tests
	python -m pipeline transform

export:     ## marts -> exports/connected_world.json + exports/world.html
	python -m pipeline export

all:        ## the whole pipeline
	python -m pipeline all

refresh:    ## re-download every source, then run everything
	python -m pipeline all --refresh

crosswalk:  ## regenerate dbt/seeds/country_aliases.csv after a source adds new names
	python scripts/build_crosswalk.py

clean:
	rm -rf data/bronze data/warehouse.duckdb dbt/target
