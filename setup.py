from setuptools import setup

setup(
    name='pera-transcript',
    version='0.1.5',    
    description='A tool to generate the unofficial transcript automatically for undergraduate students at University of Peradeniya.',
    long_description="""# Auto-Generate Tool for eng.pdn.ac.lk Interim Transcript Template (Unofficial)

## Installation

```
pip install pera-transcript
```

## Preparing metadata

Create a "metadata.yml" file with your registeration number, course registeration portal password, your date of birth, and the name of your head of department as following:

```yaml
user: E/XX/YYY # Your registeration number
passwd: xxxxxx # Your password for the course registeration / degree claim account
DOB: DD Month YYYY # Your date of birth
dept_head: Prof. John A. Doe # The name of your head of department
```

## Using the tool

1. Generate the latex file: 
```bash 
autogen_transcript /path/to/metadata.yml
```

2. Generate both latex and pdf files: 
```bash 
autogen_transcript /path/to/metadata.yml -c
``` 
or 
```bash 
autogen_transcript /path/to/metadata.yml --compile
```

* This template was originally created for the convinience of obtaining interim transcripts by [@samurdhilbk](https://github.com/samurdhilbk).

* You **must** get the interim transcript approved with the signature and seal of the head of the department.

* **Frequently Asked Questions**
  * Can I add or drop technical electvies when I am filling this?
  * Should I round off/up/down my GPA? --- the python script rounds up to the nearest 0.05
  * How can I mention me completing the internship even when TR400 results are not officially released?
  * The previous semester results are not added to the degree claim page. Can I add them to this transcript? 

  **Answer to all FAQs:** Ask the head of your department.
  
* **Disclaimer:** The creator(s) do not take any responsibility for how you ue this template or what you run into in the process, including but not limited to:
  * Head of department declining to approve this template.
  * Any institution declining to accept this unofficial transcript.
  * Mistakes you make while filling your information.
  * You intentionally filling fake information.
  * Someone using the logo or any other information in this document for any malicious purpose.

""",
    long_description_content_type='text/markdown',
    url='https://github.com/sathiiii/pera-transcript',
    author='Sathira Silva',
    author_email='sathirasofte@gmail.com',
    license='MIT License',
    packages=['pera_transcript'],
    install_requires=['pyyaml',   
                      'bs4',
                      'requests',
                      'argparse'               
                      ],
    entry_points={
        'console_scripts': ['autogen_transcript=pera_transcript.autogen_transcript:main']
    },

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)