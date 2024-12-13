import setuptools
import distutils.core

setuptools.setup(
    name='llmkey',
    version="6.0",
    install_requires=[
        "openai",
        "ollama",
        "pynput",
        "pystray",
        "pyperclip",
        "tkhtmlview",
        "appdirs",
        "PyGObject; platform_system=='Linux'" # need for pystray

    ],
    author='Read with ai',
    long_description_content_type='text/markdown',
    author_email='readwithai@gmail.com',
    license='MIT',
    keywords='LLM, GPT, clipboard',
    url='https://github.com/talwrii/llmkey',
    packages=["llmkey"],
    package_data={"llmkey": ["icon.ico"]},
    data_files=[
        ('share/applications', ['llmkey.desktop']),
        ('share/icons/hicolor/scalable/apps/', ["llmkey.svg"])
    ],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['llm-key=llmkey.serve:main']
    },
)
