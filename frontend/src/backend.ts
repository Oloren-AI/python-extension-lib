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
    paragraph: boolean;
}

export interface Bool {
    default: boolean;
}

export interface Json {
}

export interface File {
}

export interface Dir {
}

export interface Func {
}

export interface Funcs {
}

export interface Option {
    inner: Choice | Num | File | Bool | String | Json;
    _type: "Choice" | "Num" | "String" | "Bool" | "Json" | "File" | "Dir" | "Func" | "Funcs" | "VariableNumber";
}

export interface VariableNumber {
    inner: Choice | Num | File | Bool | String | Json | Option;
    initial: number;
}

export interface Ty {
    name: string;
    ty: Choice | Num | File | Bool | String | Json | Option;
    type: "Choice" | "Num" | "String" | "Bool" | "Json" | "File" | "Dir" | "Func" | "Funcs" | "Option" | "VariableNumber";
}

export interface Config {
    name: string;
    description: string | null;
    args: Array<Ty>;
    operator: string;
    num_outputs: number;
}

export const nullValue = "SPECIALNULLVALUEDONOTSETEVER";