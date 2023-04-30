# Extension Sample

This is a sample extension which implements each of the basic extension components in a simple/extensible framework.

Run via `pnpm turbo dev`

Update config.json when adding new nodes.

## Tour of the code base

The three main components are the `Dockerfile`, `core/backend`, and `core/frontend`

The Dockerfile is what is used by the AWS Elastic Cloud Service to launch the extension and maintain it in the cloud. The current Dockerfile is configured for an express server.

`core/backend` defines the endpoints which are called by dispatcher to execute the logic of the nodes.
`core/frontend` defines the components which are called by the orchestrator app to display the nodes in the Graph Editor.

### core/backend 

The logic of the nodes is defined in `core/backend/src/functions.ts`. These functions are registered via `export const FUNCTIONS...`, and are converted to endpoints in `index.ts` via ``FUNCTIONS.map((func) => { app.post(\`/operator/${func.name}`,...``.

### core/frontend

An enumeration of all component nodes defined by this extension is in `core/frontend/config.json` which should map names to components defined in `core/frontend/src/nodes/*`.

Note that we define an `operator` property which is `${baseUrl(node.remote.url)}/operator/operation` which maps to a function operator in the backend.