NAME := npuzzle

.PHONY: install test clean

install:
	@python3 -m pip install -r requirements.txt

test:
	@python3 setup.py test || true

clean:
	@python3 setup.py clean
	@rm -rf tests/__pycache__/			2> /dev/null || true
	@rm -rf core/__pycache__/				2> /dev/null || true
	@rm -rf __pycache__/						2> /dev/null || true
	@rm -rf $(NAME)/__pycache__/		2> /dev/null || true
	@rm -rf $(NAME).egg-info/ 			2> /dev/null || true
