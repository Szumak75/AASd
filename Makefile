SPHINXBUILD ?= poetry run sphinx-build
DOCS_DIR := docs
BUILD_DIR := $(DOCS_DIR)/_build

.PHONY: docs docs-clean

docs:
	$(SPHINXBUILD) -b html $(DOCS_DIR) $(BUILD_DIR)/html

docs-clean:
	rm -rf $(BUILD_DIR) $(DOCS_DIR)/_generated
