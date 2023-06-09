# Development

Let's get started building extensions.

## Setting Up Your Python Development Environment

Each extension should be in it's own github repository. Make sure you have the oloren package installed by running ` pip install oloren`.

Now, the following boilerplate code for `app.py `will get you started:

```
import oloren as olo

@olo.register(description="test")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    olo.run("sample_extension", port=5829)
```

Running `python app.py` launches your application on port 5829.

Now in the orchestrator app, using the add plugin bottom (bottom left cloud icon in graph editor), you can add this extension by adding `localhost:5829`.

## Editing

When making changes to your `app.py` file, make sure you reload the Orchestrator app. There's a few ways to do this:

1. Right click and press reload in graph editor. This should pull in new changes, but not any changes to any olo functions.
2. Remove then re-add the localhost extension. Make sure you stop and restart `app.py`.
3. Restart the entire Orchestrator app. You can do this by quitting and reopening it.

Generally removing and readding the localhost extension works well, especially when making changes to any Orchestrator functions.

## Deployment

In order to deploy your extension, it must be packaged correctly. The dependencies should be put in a `requirements.txt` file, and your repository must contain a docker file that installs all the requirements and runs the extension. Here's an example docker file:

```
FROM python:3.10-slim-bullseye
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python app.py
```

Building the extension can be done under the developer tab of the Orchestrator app. More details and specifications can be found in the packaging page.

## Requirements for Lambda Deployment

1. Must be a ubuntu docker image
2. Must use `if __name__ == "__main__":` before `olo.run`
3. Must be < 10 GB in final docker image size
4. Cannot write more than 10 GB of files (for OutputFiles etc. on one function execution)
