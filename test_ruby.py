from ruby.ruby_mainframe import Ruby
print("Initializing Ruby...")
try:
    ruby = Ruby()
    print("Ruby initialized successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
