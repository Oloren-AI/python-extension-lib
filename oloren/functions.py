def operation(node, inputs):
    if node["data"] == "Add":
        return [inputs[0] + inputs[1]]
    elif node["data"] == "Subtract":
        return [inputs[0] - inputs[1]]
    elif node["data"] == "Multiply":
        return [inputs[0] * inputs[1]]
    elif node["data"] == "Divide":
        return [inputs[0] / inputs[1]]
    
def python_eval(node, inputs):
    assert len(inputs) == len(node["data"]["inputLabels"])
    loc = {k: v for k, v in zip(node["data"]["inputLabels"], inputs)}
    exec(node["data"]["sourceCode"], loc)
    return [loc[label] for label in node["data"]["outputLabels"]]

FUNCTIONS_ = [operation, python_eval]
FUNCTIONS = {func.__name__: func for func in FUNCTIONS_}