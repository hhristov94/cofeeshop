* This project uses Python 3.11 and ```poetry```.


To run the project you need to have Docker installed and run the following commands:

```docker build -t coffeeshop_image .```

```docker run -p 8000:8000 -it coffeeshop_image uvicorn main:app --host=0.0.0.0 ```

And then you can access the app from your localhost:

http://localhost:8000/docs



**Alternatively** if you have ```poetry``` installed:

```poetry install```
```uvicorn main:app --reload ```

