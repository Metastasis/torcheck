import setuptools

setuptools.setup(
    name="torcheck",
    version="1.0.7",
    author="Dmitriy R.",
    author_email="metastasis@protonmail.ch",
    description="System for controlling and filtering traffic of Tor clients",
    long_description="System for controlling and filtering traffic of Tor clients",
    long_description_content_type="text/plain",
    packages=setuptools.find_packages(exclude=["tests*"]),
    entry_points={
        'console_scripts': [
            'torcheck-or-egress = torcheck.main_egress:main',
            'torcheck-or-ingress = torcheck.main_ingress:main',
            'torcheck-router = torcheck.main_router:main'
        ]
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    )
)
