with open(r'c:\Users\Dell\OneDrive\Desktop\SENIPLEX\memax-ott\.github\workflows\deploy.yml', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    line_112 = lines[111] # 0-indexed
    print(f"Line 112: {repr(line_112)}")
    print(f"Hex: {line_112.encode('utf-8').hex()}")
