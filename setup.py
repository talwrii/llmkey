import setuptools
import distutils.core

setuptools.setup(
    name='llmkey',
    version="1.0",
    install_requires=["openai", "pygrok"]
    author='Author',
    long_description_content_type='text/markdown',
    author_email='readwithai@gmail.com',
    description='',
    license='GPLv3',
    keywords='LLM GPT clipboard',
    url='',
    packages=[],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['llm-key=llmkey']
    },
)
