// Generated using py-ts-interfaces.
// See https://github.com/cs-cordero/py-ts-interfaces

export interface Choice {
    choices: Array<string>;
}

export interface Num {
    floating: boolean;
    min_value: number | null;
    max_value: number | null;
}

export interface String {
}

export interface File {
    allowed_extensions: Array<string> | null;
}

export interface Ty {
    name: string;
    ty: Choice | Num | File;
    type: "Choice" | "Num" | "String" | "File";
}

export interface Config {
    name: string;
    description: string | null;
    args: Array<Ty>;
    operator: string;
    num_outputs: number;
}
