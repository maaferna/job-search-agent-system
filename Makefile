# Everything CI runs, in one command:  make check
.PHONY: check sanitize links numbers spell schema test render latex

check: sanitize links numbers spell schema test render

sanitize:
	./scripts/sanitize_check.sh

links:
	python3 scripts/check_links.py

numbers:
	python3 scripts/check_numbers.py

spell:   # pip install -r requirements-dev.txt
	codespell $$(git ls-files)

schema:
	python3 reference/pipeline_check.py

test:
	python3 -m unittest discover -s tests -t .

render:
	node reference/render_test.mjs

latex:   # needs LuaLaTeX and poppler; not part of CI
	./examples/latex/build.sh all
