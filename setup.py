from setuptools import setup, find_packages

from nameko_stripe import VERSION, APP_NAME, APP_URL

setup(
    name=APP_NAME,
    version=VERSION,
    url=APP_URL,
    description='Stripe dependency for Nameko',
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
