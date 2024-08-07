import io
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def load_readme():
    with io.open(os.path.join(HERE, "README.rst"), "rt", encoding="utf8") as f:
        return f.read()


def load_about():
    about = {}
    with io.open(
        os.path.join(HERE, "tutorcloudfront", "__about__.py"),
        "rt",
        encoding="utf-8",
    ) as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about


ABOUT = load_about()


setup(
    name="tutor-contrib-cloudfront",
    version=ABOUT["__version__"],
    url="https://github.com/open-craft/tutor-contrib-cloudfront",
    project_urls={
        "Code": "https://github.com/open-craft/tutor-contrib-cloudfront",
        "Issue tracker": "https://github.com/open-craft/tutor-contrib-cloudfront/issues",
    },
    license="AGPLv3",
    author="Gabor Boros",
    author_email="gabor@opencraft.com",
    description="CloudFront plugin for Tutor",
    long_description=load_readme(),
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "tutor>=17,<19",
        "boto3",
    ],
    extras_require={
        "dev": [
            "black",
            "mypy",
            "pylint",
            "tutor[dev]>=17,<19",
        ]
    },
    entry_points={"tutor.plugin.v1": ["cloudfront = tutorcloudfront.plugin"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
