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
            "buchdashboard" = app.main:main",  # This will allow you to run the app using 'flask-app' command
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

