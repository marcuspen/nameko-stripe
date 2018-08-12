import ast
import re
from setuptools import setup, find_packages


_version_re = re.compile(r'VERSION\s+=\s+(.*)')
_app_name_re = re.compile(r'APP_NAME\s+=\s+(.*)')
_app_url_re = re.compile(r'APP_URL\s+=\s+(.*)')


def get_param(pattern):
    return ast.literal_eval(pattern.search(file_string).group(1))


with open('README.md') as readme:
    long_description = readme.read()


with open('nameko_stripe/stripe_dep.py') as f:
    file_string = f.read()
    version = get_param(_version_re)
    app_name = get_param(_app_name_re)
    app_url = get_param(_app_url_re)


setup(
    name=app_name,
    version=version,
    url=app_url,
    description='Stripe dependency for Nameko',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='marcuspen',
    author_email='me@marcuspen.com',
    install_requires=[
        'nameko>=2.0.0',
        'stripe>=2.4.0',
    ],
    extras_require={
        'dev': [
            "coverage==4.5.1",
            "flake8==3.5.0",
            "pylint==2.1.1",
            "pytest==3.7.1",
            "requests==2.19.1",
        ]
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
)
