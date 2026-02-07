.PHONY: test lint clean help

VERSION := $(shell python3 -c "import re; [print(m.group(1)) for line in open('lib/cpi_engine.py') for m in [re.match(r'VERSION\s*=\s*\"(.+?)\"', line)] if m]")

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

lint: ## Syntax check Fish + Python
	fish -n bin/claude-project-init
	python3 -m py_compile lib/cpi_engine.py
	@echo "✔ Lint passed"

test: lint ## Run smoke tests
	@echo "── --help"
	@fish bin/claude-project-init --help > /dev/null
	@echo "── --version"
	@fish bin/claude-project-init --version
	@echo "── --dry-run"
	@fish bin/claude-project-init --dry-run "Test/Smoke" --role "tester" --stack "Make" > /dev/null
	@echo "── create project"
	@rm -rf /tmp/cpi-make-test
	@fish bin/claude-project-init "Test/Make" --role "tester" --stack "Make" --output /tmp/cpi-make-test > /dev/null
	@test -f /tmp/cpi-make-test/Test-Make/README.md && echo "✔ Files generated"
	@echo "── --import"
	@fish bin/claude-project-init --import "Test/Import" --tag "Import" > /dev/null
	@echo "── --migrate"
	@fish bin/claude-project-init --migrate "Test/Migrate" --output /tmp/cpi-make-test > /dev/null
	@test -f /tmp/cpi-make-test/Test-Migrate/MIGRACAO-CHECKLIST.md && echo "✔ Migration generated"
	@echo "── cross-reference"
	@fish bin/claude-project-init "Test/XRef" --role "t" --stack "t" --output /tmp/cpi-make-test > /dev/null
	@grep -q "Test/Import" /tmp/cpi-make-test/Test-XRef/INSTRUCOES.md && echo "✔ Cross-ref OK"
	@rm -rf /tmp/cpi-make-test
	@echo ""
	@echo "✔ All tests passed"

clean: ## Remove test artifacts
	rm -rf /tmp/cpi-make-test
	rm -f lib/__pycache__/*.pyc
	rm -rf lib/__pycache__

release: lint test ## Create a release tag (usage: make release V=1.2.0)
ifndef V
	$(error Usage: make release V=1.2.0)
endif
	@echo "Tagging v$(V)..."
	git tag -a "v$(V)" -m "Release v$(V)"
	git push origin "v$(V)"
	git push origin "$$(git branch --show-current)"
	@echo "✔ Tag v$(V) pushed — GitHub Actions will create the release"

version: ## Show current version
	@echo "$(VERSION)"
