import sys

with open(r'c:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\.github\workflows\deploy.yml', 'rb') as f:
    content = f.read()
    print(content[0:2000]) # Print first 2000 bytes
