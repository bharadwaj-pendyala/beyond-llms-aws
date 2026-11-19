-include .env
export

STACK ?= beyond-llms-outreach
PY = STACK=$(STACK) PYTHONPATH=src uv run python

.PHONY: test lint local deploy setup run logs approve reject reroute color teardown

test:
	uv run pytest -q

lint:
	uv run ruff check . && uv run ruff format --check . && uv run cfn-lint template.yaml

local:
	$(PY) scripts/run_local.py $(LEADS)

deploy:
	sam build && sam deploy --guided --stack-name $(STACK) --capabilities CAPABILITY_IAM

setup:
	$(PY) scripts/setup.py

run:
	$(PY) scripts/run.py $(LEADS)

logs:
	sam logs --stack-name $(STACK) --name AppFunction --tail

approve:
	$(PY) scripts/decide.py $(LEAD) approve

reject:
	$(PY) scripts/decide.py $(LEAD) reject

reroute:
	$(PY) scripts/reroute.py $(T) $(if $(LOCAL),--local)

color:
	$(PY) scripts/color.py $(FILE)

teardown:
	$(PY) scripts/teardown.py && sam delete --stack-name $(STACK)
