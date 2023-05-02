// Generated using py-ts-interfaces.
// See https://github.com/cs-cordero/py-ts-interfaces

interface choice {
    choices: Array<string>;
}

interface num {
    floating: boolean;
    min_value: number | null;
    max_value: number | null;
}

interface file {
    allowed_extensions: Array<string> | null;
}

interface ty {
    ty: choice | num | file;
}
