# Development Workflow

0. Run `pnpm i` to install
1. Run `pnpm run dev` to start the extension. The port will default to 8080, but you can specify a different port via an environment variable (e.g. `PORT=3423 pnpm run dev`).
2. Create new nodes by adding .tsx files to the input directory.
3. Register the created nodes and relevant metadata in the `oloren.json` file.

## Notes

The name of the extension specified in the JSON config **MUST NOT** contain spaces. You may use underscores.

### JSON Configuration Exhaustive Documentation

Due to the specified `$schema` field, your editor should autocomplete and understand the format of the `oloren.json` config file. Below is some more exhaustive documentation of this specification.

#### Configuration Fields

Below is a description of each field in the configuration JSON object:

- `"name"`: This is a string that specifies the name of the extension. This field is required.
- `"version"`: This is a string that represents the version of the extension, in semver format (for example, `"1.0.0"`). The default value is `"0.0.0"`.
- `"nodes"`: This is an array of node objects that the extension uses. This field is required. See the section **Nodes Object** for details.

The configuration object should not have any additional properties not described above.

#### Nodes Object

Each object in the `"nodes"` array should have the following properties:

- `"name"`: This is a string that represents the name of the node. This field is required.

- `"path"`: This is a string that indicates the path to the module in the extension (for example, `"src/Node.tsx"`). This field is required.

- `"operator"`: This is a string representing the node operator. If the `applet` field is specified, this field is ignored.

- `"applet"`: This is an object that provides information about an applet that the node launches. See the section **Applet Object** for details.

- `"num_inputs"`: This is a number that represents the initial number of inputs. The default value is `1`.

- `"num_outputs"`: This is a number that represents the initial number of outputs. The default value is `1`.

- `"metadata"`: This field can contain any data, and represents node metadata.

The nodes object should not have any additional properties not described above.

#### Applet Object

If a node object includes an `"applet"` property, that property should be an object with the following fields:

- `"path"`: This is a string that represents the path to the applet module. This field is required.

- `"hidden"`: This is a boolean value that determines whether the applet runs on the client side without generating a user interface. The default value is `false`.

The applet object should not have any additional properties not described above.
