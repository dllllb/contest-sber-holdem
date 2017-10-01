from distutils.core import setup, Extension
from Cython.Build import cythonize

setup(
    name='holdem_win_rate',
    version='0.0.1',
    ext_modules=cythonize(
        Extension('calc_winrate',
        sources=["calc_winrate.pyx", "main.cpp"],
        language='c++',
        extra_compile_args=["-std=c++11"],
        extra_link_args=["-std=c++11"])
    )
)
