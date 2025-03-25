from setuptools import setup, find_packages

setup(
    name="buchdashboard",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.2.3",
    ],
    entry_points={
        "console_scripts": [
            "buchdashboard = app.main:main"
        ],
    },
    include_package_data=True,
    package_data={"buchdashboard":["templates/*.html","config_default.json"]},
    zip_safe=False,
)

