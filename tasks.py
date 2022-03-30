from invoke import task


@task
def test_integration(c):
    c.run("pytest ./tests/test_integration.py")


@task
def test(c):
    c.run("pytest -n auto")


@task
def lint(c):
    # fail the build if there are Python syntax errors or undefined names
    c.run("flake8 . --count --select=E9,E112,E113,E117,E711,E713,E714,F63,F7,F82 --show-source --statistics")
    # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
    c.run("flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics")
