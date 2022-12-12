# Minimal makefile for Sphinx documentation
#

# -W and --keep-going will treat warning like errors and capture all warnings.
# -n will raise warning about missing references in the docs.
SPHINXOPTS    ?= -W --keep-going -n
SPHINXBUILD   ?= sphinx-build
SPHINX_AUTOBUILD   ?= sphinx-autobuild
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

autobuild:
	$(SPHINX_AUTOBUILD) source html