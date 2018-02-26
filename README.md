# pywatch

Monitors a python file for changes and auto-reloads it.

# Setup

## UNIX Systems

1. Move the folder to your desired location
1. Create an alias in your <code>~/.bashrc</code> (Linux or MacOS) or <code>~/.bash_profile</code> (MacOS) for pywatch

# Notes

1. This module was developed for most systems, but was only tested on UNIX systems. Some features may not work on Windows systems.
1. The <code>python</code> or <code>python2</code> command must be accessible from the terminal
1. To use the <code>python2</code> command, use the -s flag
1. Files importing each other is not supported. For example, <code>test.py</code> may not import <code>test2.py</code> if <code>test2.py</code> also imports <code>test.py</code>