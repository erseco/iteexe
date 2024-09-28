from klein import Klein

app = Klein()

@app.route('/')
def home(request):
    return 'Hello, Klein!'

if __name__ == '__main__':
    app.run('localhost', 8080)
