def add(a:int , b:int) -> int:

    return a+b

print (add(3,5))

class Document:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

    def summary(self) -> str:
        return f"{self.title}: {self.content[:20]}..."
    
doc = Document("Invoice", "This is a long invoice text")
print(doc.summary())


class Car:
    def __init__(self, make:str, model:str):
        self.model = model
        self.make = make

    def summary(self) -> str:
        return f"{self.make}"

car = Car("make by amg", "g-wagan")
print(car.summary())



class Document:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def word_count(self):
        return len(self.content.split())
    
doc = Document("Invoice", "This is a long invoice text")
print(doc.word_count())


from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def read_root():
    return {"status": "ok"}