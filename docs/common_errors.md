# Common Errors and Issues

1. I cannot add the extension as a plugin

Please check the following.
1.a Make sure the extension is added as `localhost:XXXX`. For example, if you are writing your extension on a different server with VSCode, forward the post to `XXXX`.
1.b Make sure you have at least one registered function. Remember you must decorate with `@olo.register()` in order to register the function. Be sure to call the method.