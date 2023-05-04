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
    secret: boolean;
}

export interface Bool {
    default: boolean;
}

export interface File {
    allowed_extensions: Array<string> | null;
}

export interface Option {
    inner: Choice | Num | File | Bool | String;
    _type: "Choice" | "Num" | "String" | "Bool" | "File";
}

export interface Ty {
    name: string;
    ty: Choice | Num | File | Bool | String | Option;
    type: "Choice" | "Num" | "String" | "Bool" | "File" | "Option";
}

export interface Config {
    name: string;
    description: string | null;
    args: Array<Ty>;
    operator: string;
    num_outputs: number;
}

export const nullValue = "SPECIALNULLVALUEDONOTSETEVER";