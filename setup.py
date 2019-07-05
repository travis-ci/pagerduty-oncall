from setuptools import setup, find_packages


setup(
    name='pagerduty-oncall',
    version='0.1.0',
    license='MIT',
    description='This is a simple script/cron to check who is on call for a schedule/rotation and post it to Slack.',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    author='Jeroen Op \'t Eynde',
    packages=find_packages('.'),
    install_requires=['pdpyras==3.1.1',],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)
