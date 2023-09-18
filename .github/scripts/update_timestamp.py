import datetime
filename = "docs/index.md"
with open(filename, "r") as file:
    content = file.read()
    
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    content = content.replace('HOGEHOGE', timestamp)
    
    with open(filename, "w") as file:
        file.write(content)
        
