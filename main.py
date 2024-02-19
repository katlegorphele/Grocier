from userreg import app
from cli import main as cli_main

if __name__ == '__main__':
    # Start Fastapi
    import uvicorn
    uvicorn.run(app,host='localhost',port=8000)

    cli_main()