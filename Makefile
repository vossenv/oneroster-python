

ifeq ($(OS),Windows_NT)
	RM := powershell.exe -c rm -Force -Confirm:0 -Recurse -ErrorAction SilentlyContinue
else
	RM := rm -rf
endif

cleandir:
	-$(RM) dist
	-$(RM) build
	-$(RM) *.egg-info

compile:
	make cleandir
	python setup.py sdist --formats=gztar  bdist_wheel

deploy:
	make build
	twine upload dist/*.tar.gz dist/*.whl

deploy_test:
	make build
	twine upload --repository testpypi dist/*.tar.gz dist/*.whl