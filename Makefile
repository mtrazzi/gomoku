NAME := gomoku

.PHONY: install test clean

install:
	@python3 -m pip install --user -e .[dev]

lint:
	@sh ci/lint.sh

test:
	@python3 -m pytest

clean:
	@python3 setup.py clean
	@rm -rf tests/__pycache__/			2> /dev/null || true
	@rm -rf src/__pycache__/				2> /dev/null || true
	@rm -rf __pycache__/						2> /dev/null || true
	@rm -rf $(NAME)/__pycache__/		2> /dev/null || true
	@rm -rf $(NAME).egg-info/ 			2> /dev/null || true
	@cd ci
	@$(MAKE) -C docs clean