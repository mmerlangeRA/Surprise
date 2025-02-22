from codecs import open
from os import path

from setuptools import Extension, find_packages, setup

"""
Release instruction:

Update changelog and contributors list. If you ever change the
`requirements[_dev].txt`, also update the hardcoded numpy version here down
below. Or find a way to always keep both consistent.

Basic local checks:
- tests run correctly
- doc compiles without warning (make clean first).

Check that the latest RTD build was OK: https://readthedocs.org/projects/surprise/builds/

Change __version__ in setup.py to new version name. Also update the hardcoded
version in build_sdist.yml, otherwise the GA jobs will fail.

The sdist is built on 3.8 by GA:
- check the sdist building process. It should compile pyx files and the C files
  should be included in the archive
- check the install jobs. Look for compilation warnings. Make sure Cython isn't
  needed and only C files are compiled.
- check test jobs for warnings etc.

It's best to just get the sdist artifact from the job instead of re-building it
locally. Get the "false" sdist: false == with `numpy>=` constraint, not with
`oldest-supported-numpy`. We don't want `oldest-supported-numpy` as the uploaded
sdist because it's more restrictive.

Then upload to test pypi:
    twine upload blabla.tar.gz -r testpypi

Check that install works on testpypi, then upload to pypi and check again.
to install from testpypi:
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple scikit-surprise  # noqa
Doesn't hurt to check that the tests pass after installing from testpypi.

If not already done, sync gh-pages with the master's README

push new release tag on github (commit last changes first if needed):
    git tag vX.Y.Z
    git push --tags

Check that RTD has updated 'stable' to the new release (may take a while).

In the mean time, upload to conda:
    - Compute SHA256 hash of the new .tar.gz archive (or check it up on PyPI)
    - update recipe/meta.yaml on feedstock fork consequently (only version and
      sha should be changed.  Maybe add some import tests).
    - Push changes, Then open pull request on conda-forge feedstock and merge it
      when all checks are OK. Access the conda-forge feedstock it by the link on
      GitHub 'forked from blah blah'.
    - Check on https://anaconda.org/conda-forge/scikit-surprise that new
      version is available for all platforms.

Then, maybe, celebrate.
"""

from setuptools import dist  # Install numpy right now


def get_numpy_include():
    print("get_numpy_include")
    try:
        import numpy
        return numpy.get_include()
    except ImportError:
        print("no nympy")
        return ""

def get_cythonize(extensions):
    try:
        from Cython.Build import cythonize
        return cythonize(
            extensions,
            compiler_directives={
                "language_level": 3,
                "boundscheck": False,
                "wraparound": False,
                "initializedcheck": False,
                "nonecheck": False,
            },
        )
    except ImportError:
        print("Cython is not installed.")
        return extensions

def get_build_ext_cmdclass():
    try:
        from Cython.Distutils import build_ext
        return {'build_ext': build_ext}
    except ImportError:
        print("Cython is not installed.")
        return {}


""" try:
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True """
USE_CYTHON = True


__version__ = "1.1.3"

here = path.abspath(path.dirname(__file__))

# Get the long description from README.md
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    install_requires = [line.strip() for line in f.read().split("\n")]

cmdclass = {}

def build_extensions():
    print("build_extensions")

    ext = ".pyx" if USE_CYTHON else ".c"
    print("ext=",ext)

    extensions = [
        Extension(
            "surprise.similarities",
            ["surprise/similarities.pyx"],
            include_dirs=[get_numpy_include()],
        ),
        Extension(
            "surprise.prediction_algorithms.matrix_factorization",
            ["surprise/prediction_algorithms/matrix_factorization" + ext],
            include_dirs=[get_numpy_include()],
        ),
        Extension(
            "surprise.prediction_algorithms.optimize_baselines",
            ["surprise/prediction_algorithms/optimize_baselines" + ext],
            include_dirs=[get_numpy_include()],
        ),
        Extension(
            "surprise.prediction_algorithms.slope_one",
            ["surprise/prediction_algorithms/slope_one" + ext],
            include_dirs=[get_numpy_include()],
        ),
        Extension(
            "surprise.prediction_algorithms.co_clustering",
            ["surprise/prediction_algorithms/co_clustering" + ext],
            include_dirs=[get_numpy_include()],
        ),
    ]

    if USE_CYTHON:
        extensions = get_cythonize(extensions)
        global cmdclass
        cmdclass.update(get_build_ext_cmdclass())

    return extensions



print('install_requires')
print(install_requires)

setup(
    name="scikit-surprise",
    ext_modules=build_extensions(),
    author="Nicolas Hug",
    author_email="contact@nicolas-hug.com",
    description=("An easy-to-use library for recommender systems."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__version__,
    url="https://surpriselib.com",
    license="GPLv3+",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="recommender recommendation system",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    include_package_data=True,
    cmdclass=cmdclass,
    install_requires=install_requires,
    entry_points={"console_scripts": ["surprise = surprise.__main__:main"]},
)
