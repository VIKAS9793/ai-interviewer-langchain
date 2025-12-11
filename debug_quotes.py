
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    count = 0
    for i, line in enumerate(lines):
        if '"""' in line:
            print(f"{i+1}: {line.strip()}")
            count += 1
            
    print(f"Total occurrence of triple-double-quotes: {count}")
    
except Exception as e:
    print(e)
