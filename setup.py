import setuptools
import distutils.core

setuptools.setup(
    name='llmkey',
    version="1.0",
    install_requires=["openai"],
    author='Author',
    long_description_content_type='text/markdown',
    author_email='readwithai@gmail.com',
    description='',
    license='MIT',
    keywords='LLM GPT clipboard',
    url='',
    packages=["llmkey"],
    data_files=[
        ('share/applications', ['llmkey.desktop']),
        ('share/icons/hicolor/scalable/apps/', ["llmkey.svg"])
    ],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['llm-key=llmkey.serve:main']
    },
)
